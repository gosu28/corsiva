from odoo import api, fields, models


class ProductLogistic(models.Model):
    _name = 'product.logistic'

    name = fields.Char()
    shopee_logistic_id = fields.Char()

    def create_shopee_channel(self, data):
        print(data)
        vals = []
        for r in data:
            vals.append({
                'name': r['logistics_channel_name'],
                'shopee_logistic_id': r['logistics_channel_id'],
            })
        return self.create(vals)
