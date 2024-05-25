from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    shopee_category = fields.Boolean()
    shopee_cate_id = fields.Integer()
    shopee_leaf_cate = fields.Boolean()

    def create_parent_cate(self, raw_data):
        data = raw_data.copy()
        vals = []
        index = 0
        while len(raw_data) > index:
            for item in raw_data:
                index += 1
                domain = [('shopee_category', '=', True), ('shopee_cate_id', '=', item['parent_category_id'])]
                parent_category_id = self.env['product.category'].search(domain, limit=1)
                if parent_category_id:
                    val = {
                        'shopee_cate_id': item['category_id'],
                        'name': item['display_category_name'],
                        'shopee_category': True,
                        'parent_id': parent_category_id.id
                    }
                    if 'has_children' in item and item['has_children'] == False:
                        val.update(shopee_leaf_cate=True)

                    vals.append(val)
                    data.remove(item)

        if vals and data:
            self.create(vals)
            self.create_parent_cate(data)

    def create_shopee_categories(self, raw_data):
        data = raw_data.copy()
        vals = []
        for item in raw_data:
            if 'parent_category_id' in item and item['parent_category_id'] == 0:
                vals.append({
                    'shopee_cate_id': item['category_id'],
                    'name': item['display_category_name'],
                    'shopee_category': True
                })
                data.remove(item)

        self.create(vals)
        self.create_parent_cate(data)
        return True
