from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_lazada_order = fields.Boolean()
    lazada_order = fields.Char('Lazada order', readonly=False)
    # code_lazada = fields.Char('Lazada order ID', readonly=False)
    shipping_fee = fields.Monetary(
        string='Shipping fee',
        currency_field='currency_id',
        default=0,
    )

    discount = fields.Monetary(
        string='Discount',
        currency_field='currency_id',
        default=0,
    )

    totals_value = fields.Monetary(
        string='Total',
        currency_field='currency_id',
        store=True,
        compute='_compute_total_value'
    )

    request_id = fields.Char('Request ID', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_order'] = True
        return super().create(vals_list)

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id',
                 'discount', 'shipping_fee')
    def _compute_total_value(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            total = self.env['account.tax']._prepare_tax_totals(
                [x._convert_to_tax_base_line_dict() for x in order_lines],
                order.currency_id or order.company_id.currency_id,
            )
            order.totals_value = total['amount_total'] + order.shipping_fee - order.discount


