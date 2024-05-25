from odoo import api, fields, models


FIELDS = [
    'shopee_category_id',
    'description',
    'image_ids',
    'name',
    'height_amount',
    'length_amount',
    'width_amount',
    'default_code',
    'list_price',
    'weight_amount',
    'logistic_id',
]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopee_category_id = fields.Many2one('product.category')
    logistic_id = fields.Many2one('product.logistic')
    shopee_item_id = fields.Char()
    is_shopee_product = fields.Boolean()
    shopee_synced_ok = fields.Boolean()

    def action_push_product_to_shopee(self):
        return self.action_upload_product()

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get('loop', False):
            return res

        for field in FIELDS:
            if field not in vals.keys():
                continue

            for r in self:
                if not r.shopee_synced_ok:
                    continue
                r.action_update_product(vals)
            break
        return res

    def action_upload_product(self):
        connector = self.env['shopee.connector']
        img_datas = self.action_upload_images()
        result = connector.post_products(self._prepare_data_to_post_product(img_datas))
        if result:
            self.with_context(loop=True).write({
                'shopee_item_id': result['response']['item_id'],
                'shopee_synced_ok': True
            })

    def action_update_product(self, vals):
        connector = self.env['shopee.connector']
        img_datas = []
        if 'image_ids' in vals.keys():
            img_datas = self.action_upload_images()
        connector.update_products(self._prepare_data_to_post_product(img_datas))
        return True

    def _prepare_data_to_post_product(self, img_datas):
        data = {
            "brand": {
                "brand_id": 0
            },
            "category_id": self.shopee_category_id.shopee_cate_id,
            "condition": "NEW",
            "description": self.description or 'ERP product',
            "dimension": {
                "package_height": self.height_amount,
                "package_length": self.length_amount,
                "package_width": self.width_amount
            },
            "item_name": self.name,
            "item_sku": self.default_code,
            "logistic_info": [
                {
                    "enabled": True,
                    "is_free": True,
                    "logistic_id": int(self.logistic_id.shopee_logistic_id),
                    "size_id": 1
                }
            ],
            "original_price": self.list_price,
            "seller_stock": [{"stock": 0}],
            "weight": self.weight_amount
        }
        if img_datas:
            data.update(image={"image_id_list": img_datas})
        if self.shopee_item_id:
            data.update(item_id=int(self.shopee_item_id))
        return data

    def action_upload_images(self):
        connector = self.env['shopee.connector']
        img_datas = []
        for r in self.image_ids:
            img_prepare_data = {
                'image': r.raw
            }
            img_data = connector.post_images(data=img_prepare_data)
            img_datas.append(img_data['response']['image_info']['image_id'])
        return img_datas
