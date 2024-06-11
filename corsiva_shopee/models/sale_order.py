from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_shopee_order = fields.Boolean()
    shopee_order_sn = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_shopee', False):
            for vals in vals_list:
                vals['is_shopee_order'] = True
        return super().create(vals_list)

    def create_shopee_order(self, data):
        if data.get('code') == 3:
            existed_order_id = self.env['sale.order'].search([('shopee_order_sn', '=', data['data']['ordersn'])])
            if existed_order_id:
                return True

            connector = self.env['shopee.connector']
            payload = {
                'order_sn_list': data['data']['ordersn'],
                'response_optional_fields': 'total_amount,buyer_username,item_list,model_quantity_purchased'
            }

            order_data = connector.get_order_details(data=payload)
            if 'response' in order_data.keys():
                if 'order_list' in order_data['response'].keys():
                    if order_data['response']['order_list']:
                        val_api = order_data['response']['order_list'][0]
                        vals = self._prepare_vals_to_create_order(val_api)
                        self.create(vals)
            return True

    def _prepare_vals_to_create_order(self, order_data):
        partner_id = self.get_partner(order_data)
        order_line = self.get_order_line_data(order_data)
        vals = {
            'shopee_order_sn': order_data['order_sn'],
            'partner_id': partner_id.id,
            'order_line': order_line
        }
        return vals

    def get_partner(self, data):
        existed_partner_id = self.env['res.partner'].search([('name', '=', data['buyer_username'])])
        if existed_partner_id:
            return existed_partner_id

        return self.env['res.partner'].create({'name': data['buyer_username']})

    def get_order_line_data(self, data):
        vals = []
        if data.get('item_list'):
            for item in data['item_list']:
                product_id = self.get_product(item['item_id'])
                if not product_id:
                    continue
                vals.append((0, 0, {
                    'product_id': product_id,
                    'product_uom_qty': item.get('model_quantity_purchased', 1),
                    'price_unit': item['model_original_price'],
                }))
        return vals

    def get_product(self, item_id):
        product_id = self.env['product.template'].search([('shopee_item_id', '=', item_id)])
        if product_id:
            return product_id.id
        return False
