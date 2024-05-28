from odoo import api, fields, models


class ProductLogistic(models.Model):
    _name = 'product.logistic'

    name = fields.Char()
    shopee_logistic_id = fields.Char()
    line_ids = fields.One2many('product.logistic.line', 'line_id')
    size_id = fields.Char()
    shipping_fee = fields.Float()

    def create_shopee_channel(self, data):
        vals = []
        for r in data:
            if not r['enabled'] or r['mask_channel_id'] != 0:
                continue
            line_ids = self._prepare_data_for_line(r['size_list'])
            vals.append({
                'name': r['logistics_channel_name'],
                'shopee_logistic_id': r['logistics_channel_id'],
                'size_id': r['fee_type'],
                'line_ids': line_ids
            })
        return self.create(vals)

    def _prepare_data_for_line(self, data):
        res = []
        for r in data:
            res.append((0, 0, r))
        return res


class ProductLogisticLine(models.Model):
    _name = 'product.logistic.line'

    line_id = fields.Many2one('product.logistic')
    size_id = fields.Char()
    name = fields.Char()
    default_price = fields.Float()
