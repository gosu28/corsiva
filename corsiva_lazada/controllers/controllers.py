# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.addons.corsiva_connector.models import common
from odoo import http
from odoo.http import request
# from

import requests
import json


class LazadaControllers(http.Controller):

    @http.route('/lazada_auth/', type='http', auth="none")
    def index(self, **kw):
        code = kw.get('code')
        if code:
            connector = request.env['corsiva.connector'].sudo().open(connector_type='lazada')
            data = connector.create_access_token('create_access_token', code)
            self.save_auth_data(data)

        action_id = request.env['ir.actions.actions'].sudo().search([('name', '=', 'Lazada Settings')]).id
        menu_id = request.env['ir.ui.menu'].sudo().search([('name', '=', 'Lazada')]).id
        if action_id and menu_id:
            url = '/web?db=%s#action=%s&model=res.config.settings&view_type=form&cids=1&menu_id=%s' % (request.env.cr.dbname, action_id, menu_id)
        else:
            url = '/web'

        return request.redirect(url)

    @http.route('/webhook-lazada', type='json', auth='public', csrf=False, methods=['POST'])
    def lazada_webhook_handler(self, **post):

        try:
            data = json.loads(request.httprequest.data)
            lazada_order_id = data['data']['trade_order_id']
            connector = request.env['corsiva.connector'].sudo().open(connector_type='lazada')
            response_data = connector.get_order_items(action='get_order_items', lazada_order_id=lazada_order_id)
        except ValueError as e:
            return http.Response('Invalid JSON', status=400)
        self.create_order(order=response_data, order_id=lazada_order_id)
        return http.Response('OK', status=200)

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()
        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])

    def create_order(self, order, order_id):
        if order['code'] == '0':
            orders = request.env['sale.order'].sudo()
            check_order = orders.search([('lazada_order', '=', order_id)])
            if not check_order:
                order_id = orders.create({
                    'partner_id': self._create_customer(order['data'][0]['buyer_id']).id,
                    'is_lazada_order': True,
                    'lazada_order': order['data'][0]['order_id'],
                    'request_id': order['request_id']
                })
                for item in order['data']:
                    # pending
                    if item['status'] == 'pending':
                        product = request.env['product.template'].sudo().search([('item_id', '=', item['product_id'])])
                        order_id.order_line = [(0, 0, {'product_id': product.product_variant_id.id})]
                        for order_line in order_id.order_line:
                            if order_line.product_id.id == product.product_variant_id.id:
                                order_line.product_uom_qty = order_line.product_uom_qty + 1
                                order_id.shipping_fee = order_id.shipping_fee + item['shipping_amount']
                                order_id.discount = order_id.discount + item['voucher_amount']
                            else:
                                order_id.order_line = [(4, 0, {'product_id': product.product_variant_id.id,
                                                               'product_uom_qty': 1})],
                order_id.order_line.tax_id = None
                order_id.action_confirm()

    def get_order(self, lazada_order_id):
        try:
            connector = request.env['corsiva.connector'].sudo().open(connector_type='lazada')
            response_data = connector.get_order(action='get_order', lazada_order_id=lazada_order_id)
            # if order['status'] == 'ready_to_ship':
        except ValueError as e:
            return http.Response('Invalid JSON', status=400)
        if response_data['code'] == '0':
            return response_data['data']
        else:
            return []

    @staticmethod
    def _create_customer(buyer_id):
        check_customer = request.env['res.partner'].sudo().search([('name', '=', buyer_id)])

        if check_customer:
            return check_customer
        else:
            vals = {
                'name': str(buyer_id),
                'is_company': False
                }
            customer_id = request.env['res.partner'].sudo().create(vals)
            return customer_id


# Lazada
# seller
# mailinh1506@gmail.com
# Linh@123456


