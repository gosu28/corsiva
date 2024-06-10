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

    def create_shopee_order(self, data):
        if data.get('code') == 3:
            connector = self.env['shopee.connector']
            # if data['data']['status'] == 'PROCESSED':
            payload = {
                'order_sn_list': data['data']['ordersn'],
                'request_order_status_pending': True,
                'response_optional_fields': 'total_amount'
            }

            order_data = connector.get_order_details(data=payload)
            vals = self._prepare_vals_to_create_order(order_data)
            self.create(vals)

    def _prepare_vals_to_create_order(self, order_data):
        partner_id = self.get_partner(order_data)
        order_line = self.get_order_line_data(order_data)
        vals = {
            'partner_id': partner_id,
            'order_line': order_line
        }
        return vals

    def get_partner(self, data):
        existed_partner_id = self.env['res.partner'].search([('name', '=', data['buyer_username'])])
        if existed_partner_id:
            return existed_partner_id

        vals = {
            # 'buyer_user_id': data['buyer_user_id'],
            'name': data['buyer_username'],
        }
        return self.env['res.partner'].create(vals)

    def get_order_line_data(self, data):
        vals = []
        if data.get('item_list'):
            for item in data['item_list']:
                product_id = self.get_product(item['item_id'])
                if not product_id:
                    continue
                vals.append((0, 0, {
                    'product_id': product_id,
                    'model_original_price': item['model_original_price'],
                }))
        return vals

    def get_product(self, item_id):
        product_id = self.env['product.template'].search([('shopee_item_id', '=', item_id)])
        if product_id:
            return product_id.id
        return False
