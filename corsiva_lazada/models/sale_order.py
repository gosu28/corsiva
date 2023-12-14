from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_lazada_order = fields.Boolean()
    lazada_order = fields.Char('Lazada order', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_order'] = True
        return super().create(vals_list)
