from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_shopee_order = fields.Boolean(copy=False)
    shopee_order_sn = fields.Char(string='Shopee Order ID', copy=False)
    shopee_order_status = fields.Char(copy=False)

    def create_shopee_order(self, data):
        if data.get('code') == 3:
            existed_order_id = self.env['sale.order'].search([('shopee_order_sn', '=', data['data']['ordersn'])])
            if existed_order_id:
                return True
            return self.create_new_sale_order(data)

    def create_new_sale_order(self, data):
        connector = self.env['shopee.connector']
        payload = {
            'order_sn_list': data['data']['ordersn'],
            'request_order_status_pending': True,
            'response_optional_fields': 'buyer_username,item_list,actual_shipping_fee,estimated_shipping_fee'
        }

        order_data = connector.get_order_details(data=payload)
        if 'response' not in order_data.keys() or 'order_list' not in order_data['response'].keys():
            return True

        if order_data['response']['order_list']:
            val_api = order_data['response']['order_list'][0]
            vals = self._prepare_vals_to_create_order(val_api)
            if vals:
                self.create(vals)

    def _prepare_vals_to_create_order(self, order_data):
        partner_id = self.get_partner(order_data)
        order_line, discount_price = self.get_order_line_data(order_data)

        if not order_line:
            return {}

        return {
            'is_shopee_order': True,
            'shipping_fee': order_data.get('estimated_shipping_fee', 0),
            'discount': discount_price,
            'shopee_order_status': order_data['order_status'],
            'shopee_order_sn': order_data['order_sn'],
            'partner_id': partner_id.id,
            'order_line': order_line
        }

    def get_partner(self, data):
        existed_partner_id = self.env['res.partner'].search([('name', '=', data['buyer_username'])])
        if existed_partner_id:
            return existed_partner_id

        return self.env['res.partner'].create({'name': data['buyer_username']})

    def get_order_line_data(self, data):
        vals = []
        discount_price = 0
        if 'item_list' not in data.keys():
            return vals, discount_price

        for item in data['item_list']:
            product_id = self.get_product(item['item_id'])
            if not product_id:
                continue
            discount_price += item['model_original_price'] - item['model_discounted_price']
            vals.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': item['model_quantity_purchased'],
                'price_unit': item['model_original_price'],
            }))
        return vals, discount_price

    def get_product(self, item_id):
        product_id = self.env['product.template'].search([('shopee_item_id', '=', item_id)], limit=1)
        print(item_id)
        print(product_id)
        if product_id:
            return product_id.id
        return False
