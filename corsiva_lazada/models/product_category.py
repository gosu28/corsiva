from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lazada_category_id = fields.Char()
    is_lazada = fields.Boolean()
    is_leaf = fields.Boolean()

    def flatten_tree_data(self, data, parent_category_id=None, level=0):
        flattened_data = []

        for item in data:
            flattened_item = {
                'category_id': item['category_id'],
                'name': item.get('name', False),
                'leaf': item['leaf'],
                'parent_category_id': parent_category_id,
                'level': level
            }
            flattened_data.append(flattened_item)

            if 'children' in item and item['children']:
                child_data = self.flatten_tree_data(item['children'], item['category_id'], level + 1)
                flattened_data.extend(child_data)

        return flattened_data

    def create_categories(self, datas, parent_id=False):
        values = []
        for data in datas:
            if not data['name']:
                continue
            values.append({
                'name': data['name'],
                'lazada_category_id': data['category_id'],
                'parent_id': parent_id,
                'is_leaf': data['leaf'],
                'is_lazada': True
            })
        self.create(values)

    def _build_dict_for_child_category(self, category_ids):
        res = {}
        for category_id in category_ids:
            res[category_id.lazada_category_id] = category_id.id
        return res

    def create_correspond_categories(self, data):
        grouped_data = self.flatten_tree_data(data)

        data_dict = {}
        parent_list = []
        for record in grouped_data:
            level = record['level']
            if level == 0:
                parent_list.append(record)
                continue

            if level not in data_dict.keys():
                data_dict[level] = {}

            parent_category_id = record['parent_category_id']
            if parent_category_id not in data_dict[level].keys():
                data_dict[level][parent_category_id] = []
            data_dict[level][parent_category_id].append(record)

        if parent_list:
            self.create_categories(parent_list)

        for key in data_dict.keys():
            domain = [('lazada_category_id', 'in', list(data_dict[key].keys()))]
            parent_category_ids = self.search(domain)
            parent_category_dict = self._build_dict_for_child_category(parent_category_ids)
            for child_key in data_dict[key].keys():
                if str(child_key) not in list(parent_category_dict.keys()):
                    continue
                self.create_categories(data_dict[key][child_key], parent_id=parent_category_dict[str(child_key)])

        return True
