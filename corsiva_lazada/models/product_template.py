import hashlib
import hmac
import json
from datetime import datetime

import requests

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_lazada_product = fields.Boolean()
    image_ids = fields.One2many(
        'ir.attachment',
        'lazada_product_id',
        'Images'
    )

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_product'] = True
        res = super().create(vals_list)
        res.create_product()
        return res

    def write(self, vals):
        self.create_product()
        return super().write(vals)

    def create_product(self):
        connector = self.env['corsiva.connector'].open(connector_type='lazada')
        # images_data = connector.create_images(action='create_images', data=self.image_ids)
        category_data = connector.get_categories(action='get_categories')
        self.convert_raw_data(category_data['data'])

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
                'is_lazada': True
            })
        self.env['product.category'].create(values)
    
    def _build_dict_for_child_category(self, category_ids):
        res = {}
        for category_id in category_ids:
            res[category_id.lazada_category_id] = category_id.id
        return res

    def convert_raw_data(self, data):
        grouped_data = self.flatten_tree_data(data)

        data_dict = {}
        parent_list = []
        max_level = 0
        for record in grouped_data:
            level = record['level']

            if level > max_level:
                max_level = level

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
            parent_category_ids = self.env['product.category'].search(domain)
            parent_category_dict = self._build_dict_for_child_category(parent_category_ids)
            for child_key in data_dict[key].keys():
                try:
                    self.create_categories(data_dict[key][child_key], parent_id=parent_category_dict.get(str(child_key), False))
                except Exception as e:
                    print(child_key)
                    print(data_dict[key][child_key])





