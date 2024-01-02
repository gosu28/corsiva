# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.addons.corsiva_connector.models import common
from odoo import http
from odoo.http import request
# from

import requests
import json
import time


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
        request.env['sale.order'].with_delay().create_order(order=response_data, lazada_order=lazada_order_id)
        return http.Response('OK', status=200)

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()
        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])

    # 450476244569495

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



# Lazada
# seller
# mailinh1506@gmail.com
# Linh@123456


