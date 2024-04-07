from odoo import api, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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

    type_ecommerce = fields.Many2many("corsiva.ecommerce", string='Ecommerce')

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

    def add_type_ecommerce(self, name=None):
        type_ecommerce = self.env["corsiva.ecommerce"].search([("name", "=", name)])
        if type_ecommerce:
            for item in type_ecommerce:
                self.type_ecommerce = (4, item.id)
        else:
            type_ecommerce = self.env["corsiva.ecommerce"].create({
                "name": name,
                "description": name,
            })
            self.type_ecommerce = (4, type_ecommerce.id)