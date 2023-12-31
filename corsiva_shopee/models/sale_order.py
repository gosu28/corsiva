from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_shopee_order = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_shopee', False):
            for vals in vals_list:
                vals['is_shopee_order'] = True
        return super().create(vals_list)
