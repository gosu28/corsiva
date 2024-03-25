from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime
import pytz


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_woo = fields.Boolean(string="Is Woo", default=False)
    url_product = fields.Char('URL Product Woo')
    woo_sku = fields.Char('SKU WOO', readonly=True)
    woo_type = fields.Selection([
        ('simple', 'Simple Product'),
        ('grouped', 'Grouped Product'),
        ('virtual', 'Virtual Product'),
        ('downloadable', 'Downloadable Product'),
        ('external/affiliate', 'external/affiliate Product'),
        ('variable product', 'Variable Product'),
        ], string='Product Woo Type', default='simple', required=True)

    woo_status = fields.Selection([
        ('publish', 'Published'),
        ('pending', 'Pending Review'),
        ('draft', 'Draft'),
        ], string='Product Woo Status', default='publish', required=True)

    woo_image_ids = fields.Many2many(
        'ir.attachment',
        'product_template_ir_attachment_rel',
        string='Upload Images'
    )
    woo_image_kanban_ids = fields.Many2many(
        'ir.attachment',
        'product_template_kanban_ir_attachment_rel',
        compute='_compute_woo_image_kanban_ids',
        inverse='_inverse_woo_image_kanban_ids',
        ondelete='cascade',
        store=True
    )

    @api.depends('lazada_image_ids')
    def _compute_woo_image_kanban_ids(self):
        for r in self:
            r.lazada_image_kanban_ids = r.lazada_image_ids.ids

    def _inverse_woo_image_kanban_ids(self):
        for r in self:
            r.lazada_image_ids = r.lazada_image_kanban_ids.ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if not r.is_woo and not r.env.context.get('default_is_woo_product', False):
                continue
            r.lazada_image_kanban_ids.public_image()
            r.lazada_image_ids.public_image()
            r.woo_sku = r.get_sku_woo()
        return res

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


    def action_push_product_to_shop(self, action):
        connector = self.env['corsiva.woo'].open(connector_type='woo')
        products_prepare_data = self.prepare_data_to_push_product()

        if action == 'create':
            response_data = connector.woo_create_product(data=products_prepare_data)
        elif action == 'update':
            connector.update_products(action='update_products', data=products_prepare_data)

        return True

    def prepare_data_to_push_product(self):
        data = {
            "name": self.name or "",
            "type": self.woo_type,
            "regular_price": str(self.list_price) or "",
            "description": self.description or "",
            "short_description": self.short_description or "",
            "categories": [],
            "images": self.get_images_url() or [],
            "status": self.woo_status or "",
            "sku": self.woo_sku or "",
            "weight": str(self.weight_amount) or "",
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

    
