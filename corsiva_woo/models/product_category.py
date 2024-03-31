from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    woo_category_id = fields.Char(string='Woo ID')
    is_woo = fields.Boolean()
    # is_leaf = fields.Boolean(string='Leaf Category')
    slug = fields.Char(string='Slug', readonly=True)
    woo_parent_id = fields.Char(string='Woo Parent ID')
    description = fields.Text(string='Description')

    def flatten_tree_data(self, data, level=0):
        flattened_data = []

        for item in data:
            flattened_item = {
                'woo_category_id': item['id'],
                'name': item.get('name', False),
                'slug': item.get('slug', False),
                'description': item.get('description', False),
                'parent_category_id': item.get('parent', False),
                'level': level
            }
            flattened_data.append(flattened_item)
        return flattened_data

    def create_categories(self, datas, parent_id=False):
        values = []
        for data in datas:
            if not data['name']:
                continue
            check_unique = self.env['product.category'].search([("woo_category_id", "=", data['woo_category_id']),
                                                                ("slug", "=", data['slug'])])
            if not check_unique:
                values.append({
                    'name': data['name'],
                    'woo_category_id': data['woo_category_id'],
                    'parent_id': parent_id,
                    'slug': data['slug'],
                    'description': data['description'],
                    'is_woo': True
                })
        self.create(values)

    def add_parent_category(self, data):
        for item in data:
            if item["parent_category_id"]:
                parent_n = self.env['product.category'].search([("woo_category_id", "=",
                                                                     item['woo_category_id'])])
                parent_n1 = self.env['product.category'].search([("woo_category_id", "=",
                                                                 item['parent_category_id'])])

                parent_n.parent_id = parent_n1.id

    def create_correspond_categories(self, data):
        grouped_data = self.flatten_tree_data(data)
        self.create_categories(grouped_data)
        self.add_parent_category(grouped_data)
        return True





