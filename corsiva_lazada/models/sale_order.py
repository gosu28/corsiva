from odoo import api, fields, models
from odoo.tools.misc import formatLang

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

    # totals_value = fields.Monetary(
    #     string='Total',
    #     currency_field='currency_id',
    #     store=True,
    #     compute='_compute_tax_totals'
    # )

    request_id = fields.Char('Request ID', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_order'] = True
        return super().create(vals_list)

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'currency_id',
                 'discount', 'shipping_fee')
    def _compute_tax_totals(self):
        for order in self:
            super(SaleOrder, order)._compute_tax_totals()
            tax_totals = order.tax_totals
            tax_totals['amount_total'] += order.shipping_fee - order.discount
            tax_totals['amount_untaxed'] = tax_totals['amount_total']
            tax_totals['formatted_amount_total'] = formatLang(order.env, tax_totals['amount_total'],
                                                              currency_obj=order.currency_id)
            tax_totals['formatted_amount_untaxed'] = formatLang(order.env, tax_totals['amount_untaxed'],
                                                                currency_obj=order.currency_id)
            order.tax_totals = tax_totals

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total',
                 'discount', 'shipping_fee')
    def _compute_amounts(self):
        for order in self:
            super(SaleOrder, order)._compute_amounts()
            order.amount_total += order.shipping_fee - order.discount






