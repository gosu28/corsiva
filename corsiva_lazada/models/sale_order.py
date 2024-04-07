from odoo import api, fields, models
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_lazada_order = fields.Boolean()
    lazada_order = fields.Char('Lazada order', readonly=False)

    request_id = fields.Char('Request ID', readonly=False)

    _sql_constraints = [
        ('lazada_order',
         'unique(lazada_order)',
         'Choose another lazada_order value - it has to be unique!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_order'] = True
        return super().create(vals_list)

    def create_order(self, order, lazada_order):
        if order['code'] == '0':
            orders = self.env['sale.order'].sudo()
            check_order = orders.search([('lazada_order', '=', lazada_order)])
            if not check_order and order['data'][0]['status'] == 'pending':
                order_id = orders.create({
                    'partner_id': self._create_customer(order['data'][0]['buyer_id']).id,
                    'is_lazada_order': True,
                    'lazada_order': order['data'][0]['order_id'],
                    'request_id': order['request_id']
                })
                for item in order['data']:
                    # pending
                    # ready_to_ship
                    product = self.env['product.template'].sudo().search([('item_id', '=', item['product_id'])])
                    if order_id.order_line:
                        for order_line in order_id.order_line:
                            if order_line.product_id.id == product.product_variant_id.id:
                                order_line.product_uom_qty = order_line.product_uom_qty + 1
                                order_id.shipping_fee = order_id.shipping_fee + item['shipping_amount']
                                order_id.discount = order_id.discount + item['voucher_amount']
                            else:
                                order_id.order_line = [(4, 0, {'product_id': product.product_variant_id.id,
                                                               'product_uom_qty': 1})]
                    else:
                        order_id.order_line = [(0, 0, {'product_id': product.product_variant_id.id})]
                        order_id.shipping_fee = order_id.shipping_fee + item['shipping_amount']
                        order_id.discount = order_id.discount + item['voucher_amount']
                order_id.order_line.tax_id = None
                order_id.action_confirm()

    def _create_customer(self, buyer_id):
        check_customer = self.env['res.partner'].sudo().search([('name', '=', buyer_id)])

        if check_customer:
            return check_customer
        else:
            vals = {
                'name': str(buyer_id),
                'is_company': False
                }
            customer_id = self.env['res.partner'].sudo().create(vals)
            return customer_id
