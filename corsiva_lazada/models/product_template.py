from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _category_domain(self):
        if self.env.context.get('default_is_lazada_product', False):
            return [('is_leaf', '=', True)]
        return [('is_lazada', '=', False)]

    is_lazada_product = fields.Boolean()
    image_ids = fields.One2many(
        'ir.attachment',
        'lazada_product_id',
        'Images'
    )
    categ_id = fields.Many2one(
        'product.category',
        'Product Category',
        change_default=True,
        default=False,
        domain=_category_domain,
        group_expand='_read_group_categ_id',
        required=True
    )
    weight_amount = fields.Float(default=10)
    weight_uom_name = fields.Char(default='kg', readonly=1)
    height_amount = fields.Float(default=10)
    height_uom_name = fields.Char(default='cm', readonly=1)
    length_amount = fields.Float(default=10)
    length_uom_name = fields.Char(default='cm', readonly=1)
    width_amount = fields.Float(default=10)
    width_uom_name = fields.Char(default='cm', readonly=1)
    # lazada fields
    shop_sku = fields.Char()
    sku_id = fields.Char()

    @api.constrains('weight_amount', 'height_amount', 'length_amount', 'width_amount', 'image_ids')
    def _constrains_product_dimensions(self):
        for r in self:
            if r.weight_amount == 0 or r.height_amount == 0 or r.length_amount == 0 or r.width_amount == 0:
                raise ValidationError('Error: ')
            if not r.image_ids:
                raise ValidationError('Error: You need to set image for this products')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if not r.is_lazada_product:
                continue
            r.action_push_product_to_shop(action='create')
        return res

    def write(self, vals):
        res = super().write(vals)
        if not self.env.context.get('loop', False):
            for r in self:
                if not r.is_lazada_product:
                    continue
                r.action_push_product_to_shop(action='update')
        return res

    def action_push_product_to_shop(self, action):
        connector = self.env['corsiva.connector'].open(connector_type='lazada')
        image_datas = self.create_images(connector)
        products_prepare_data = self.prepare_data_to_push_product(action, image_datas)
        if action == 'create':
            response_data = connector.create_products(action='create_products', data=products_prepare_data)['data']
            self.with_context(loop=True).write({
                'shop_sku': response_data['sku_list'][0]['shop_sku'],
                'sku_id': response_data['sku_list'][0]['sku_id'],
            })
        elif action == 'update':
            connector.update_products(action='update_products', data=products_prepare_data)

    def create_images(self, connector):
        img_datas = []
        for r in self.image_ids:
            img_prepare_data = self._prepare_data_to_create_images(r)
            img_data = connector.create_images(action='create_images', data=img_prepare_data)
            img_datas.append(img_data['data'])
        return img_datas

    @staticmethod
    def _prepare_data_to_create_images(attachment_id):
        return {
            'image': attachment_id.raw
        }

    def prepare_data_to_push_product(self, action, img_datas):
        data = {
            "Request": {
                "Product": {
                    "PrimaryCategory": self.categ_id.lazada_category_id,
                    "Images": {
                        "Image": [data['image']['url'] for data in img_datas]
                    },
                    "Attributes": {
                        "name": self.name,
                        "short_description": self.description,
                        "brand": "No Brand",
                        "brand_id": "65074"  # fixed id for 'No Brand'
                    },
                    "Skus": {
                        "Sku": [{
                            "SellerSku": self.default_code,
                            "quantity": "1",
                            "price": self.list_price,
                            "package_height": self.height_amount,
                            "package_length": self.length_amount,
                            "package_width": self.width_amount,
                            "package_weight": self.weight_amount,
                            "Images": {"Image": []}
                        }]
                    }
                }
            }
        }
        if action == 'update':
            data['Request']['Product']['Skus']['Sku'][0]['SkuId'] = self.sku_id
        return data

    def _prepare_data_to_update_product(self, img_datas):
        return {
            "Request": {
                "Product": {
                    "PrimaryCategory": self.categ_id.lazada_category_id,
                    "Images": {
                        "Image": [data['image']['url'] for data in img_datas]
                    },
                    "Attributes": {
                        "name": self.name,
                        "short_description": self.description,
                        "brand": "No Brand",
                        "brand_id": "65074"  # fixed id for 'No Brand'
                    },
                    "Skus": {
                        "Sku": [{
                            "SkuId": self.sku_id,
                            "SellerSku": self.default_code,
                            "quantity": "1",
                            "price": self.list_price,
                            "package_height": self.height_amount,
                            "package_length": self.length_amount,
                            "package_width": self.width_amount,
                            "package_weight": self.weight_amount,
                            "Images": {"Image": []}
                        }]
                    }
                }
            }
        }
