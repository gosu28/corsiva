from odoo import api, fields, models, tools


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

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for r in res:
            if not r.is_lazada_product:
                continue
            r.action_push_product_to_shop()
        return res

    def write(self, vals):
        res = super().write(vals)
        for r in self:
            if not r.is_lazada_product:
                continue
            r.action_push_product_to_shop()
        return res

    def action_push_product_to_shop(self):
        connector = self.env['corsiva.connector'].open(connector_type='lazada')
        
        image_datas = []
        if self.image_ids:
            image_datas = self.create_images(connector)

        products_prepare_data = self._prepare_data_to_action_push_product_to_shops()
        connector.action_push_product_to_shops(action='create_products', data=products_prepare_data)
    
    def create_images(self, connector):
        img_datas = []
        for r in self.image_ids:
            img_prepare_data = self._prepare_data_to_create_images(r)
            img_data = connector.create_images(action='create_images', data=img_prepare_data)
            img_datas.append(img_data)
        return img_datas

    @staticmethod
    def _prepare_data_to_create_images(attachment_id):
        return {
            'image': attachment_id.raw
        }

    def _prepare_data_to_action_push_product_to_shops(self):
        return {
            "Request": {
                "Product": {
                    "PrimaryCategory": self.categ_id.lazada_category_id,
                    "AssociatedSku": "Existing SkuId in seller center",
                    "Images": {
                        "Image": []
                    },
                    "Attributes": {
                        "propCascade": {
                            "26": "120013644:162,100006867:160387"
                        },
                        "name": "test 2022 02",
                        "disableAttributeAutoFill": False,
                        "description": "TEST",
                        "brand": "No Brand",
                        "brand_id": "30768",
                        "model": "test",
                        "waterproof": "Waterproof",
                        "warranty_type": "Local seller warranty",
                        "warranty": "1 Month",
                        "short_description": "",
                        "Hazmat": "None",
                        "material": "Leather",
                        "laptop_size": "11 - 12 inches",
                        "delivery_option_sof": "No",
                        "gift_wrapping": "Yes",
                        "name_engravement": "Yes",
                        "preorder_enable": "Yes",
                        "preorder_days": "25"
                    },
                    "Skus": {
                        "Sku": [
                            {
                                "SellerSku": "test2022 02",
                                "saleProp": {
                                    "color_family": "Green",
                                    "size": "10"
                                },
                                "quantity": "3",
                                "price": "35",
                                "special_price": "33",
                                "special_from_date": "2022-06-20 17:18:31",
                                "special_to_date": "2025-03-15 17:18:31",
                                "package_height": "10",
                                "package_length": "10",
                                "package_width": "10",
                                "package_weight": "0.5",
                                "package_content": "laptop bag",
                                "Images": {
                                    "Image": []
                                }
                            }
                        ]
                    }
                }
            }
        }
