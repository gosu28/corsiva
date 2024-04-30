from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime
import pytz


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _category_domain_woo(self):
        return [('is_woo', '=', True)]

    is_woo = fields.Boolean(string="Is Woo", default=False)
    url_product = fields.Char('URL Product Woo')
    woo_sku = fields.Char('SKU WOO', readonly=True)
    id_woo = fields.Char('id woo', readonly=True)
    woo_synced_ok = fields.Boolean(String="Sync woo ok", readonly=True, default=False)
    woo_type = fields.Selection([
        ('simple', 'Simple Product'),
        ('grouped', 'Grouped Product'),
        ('external', 'external/affiliate Product'),
        ('variable', 'Variable Product'),
        ], string='Product Woo Type', default='simple', required=True)

    woo_status = fields.Selection([
        ('publish', 'Published'),
        ('pending', 'Pending Review'),
        ('draft', 'Draft'),
        ('private ', 'Private'),
        ], string='Product Woo Status', default='publish', required=True)

    woo_image_ids = fields.Many2many(
        'ir.attachment',
        'product_template_ir_attachment_rel',
        string='Upload Images'
    )
    is_manage_stock = fields.Boolean(string='Stock Management', compute='compute_woo_manage_stock', readonly=True)
    woo_image_kanban_ids = fields.Many2many(
        'ir.attachment',
        'product_template_kanban_ir_attachment_rel',
        compute='_compute_woo_image_kanban_ids',
        inverse='_inverse_woo_image_kanban_ids',
        ondelete='cascade',
        store=True
    )

    woo_categ_id = fields.Many2one(
        'product.category',
        'Woo Category',
        change_default=True,
        default=False,
        domain=_category_domain_woo,
        group_expand='_read_group_categ_id',
    )

    @api.depends('detailed_type')
    def compute_woo_manage_stock(self):
        for res in self:
            if res.detailed_type == "product":
                self.is_manage_stock = True
            else:
                self.is_manage_stock = False

    @api.depends('woo_image_ids')
    def _compute_woo_image_kanban_ids(self):
        for r in self:
            r.woo_image_kanban_ids = r.woo_image_ids.ids

    def _inverse_woo_image_kanban_ids(self):
        for r in self:
            r.woo_image_ids = r.woo_image_kanban_ids.ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if not r.is_woo:
                continue
            r.woo_image_kanban_ids.public_image()
            r.woo_image_ids.public_image()
            # r.woo_sku = r.get_sku_woo()
            # r.add_locations()
        return res

    # def add_locations(self):
    #     for res in self:
    #         location_id = res.env.ref('corsiva_lazada.lazada_stock_location')
    #         res.location_id = location_id.id

    def write(self, vals):
        res = super().write(vals)
        if "woo_image_kanban_ids" in vals or "woo_image_ids" in vals:
            self.woo_image_kanban_ids.public_image()
            self.woo_image_ids.public_image()
        if self.is_woo and self.woo_synced_ok:
            self.action_push_product_to_shop(action="update")

    def get_sku_woo(self, timezone='Asia/Kolkata'):
        for res in self:
            format = "%Y%m%d%H%M%S%Z%z"
            # getting the standard UTC time
            original_tz = pytz.timezone(timezone)
            # Getting the current time in the Asia/Kolkata Time Zone
            datetime_object = datetime.now(original_tz)
            sku_key = "WOO" + str(res.id) + datetime_object.strftime(format)
            return sku_key

    def action_create_product_woo(self):
        for r in self:
            r.action_push_product_to_shop(action="create")
            r.is_woo = True
            r.woo_synced_ok = True
            r.add_type_ecommerce(name="WooEcommerce")

    def action_push_product_to_shop(self, action):
        connector = self.env['corsiva.woo'].open(connector_type='woo')
        products_prepare_data = self.prepare_data_to_push_product()

        if action == 'create':
            response_data = connector.woo_create_product(data=products_prepare_data)
            self.with_context(loop=True).write({
                'id_woo': response_data['id'],
                "url_product": response_data['permalink']
            })
        elif action == 'update':
            connector.woo_update_product(data=products_prepare_data, id_woo=self.id_woo)
        return True

    def get_categories_id(self):
        categories = []
        for res in self:
            categories.append({"id": self.woo_categ_id.woo_category_id})
            return categories

    def prepare_data_to_push_product(self):
        data = {
            "name": self.name or "",
            "type": self.woo_type,
            "regular_price": str(self.list_price) or "",
            "description": self.description or "",
            "short_description": self.short_description or "",
            "categories": self.get_categories_id(),
            "images": self.get_images_url() or [],
            "status": self.woo_status or "",
            "sku": self.default_code,
            "weight": str(self.weight_amount) or "",
            "manage_stock": self.is_manage_stock,
            "dimensions": {
                "length": str(self.length_amount) or "",
                "width": str(self.width_amount) or "",
                "height": str(self.height_amount) or "",
            },
        }
        return data

    def get_images_url(self):
        images = []
        for res in self.lazada_image_ids:
            img_url = "/web/image/ir.attachment/{0}/raw/{1}".format(res.id, res.name)
            url_base = self.env['ir.config_parameter'].get_param('web.base.url')
            url_product = url_base + img_url
            img = {"src": url_product}
            images.append(img)
        return images

    
