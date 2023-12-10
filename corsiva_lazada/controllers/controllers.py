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

    @http.route('/webhook-lazada', type='http', auth='public', csrf=False, methods=['POST'])
    def lazada_webhook_handler(self, **post):

        try:
            data = json.loads(request.httprequest.data)
            lazada_order_id = data['data']['trade_order_id']
            connector = request.env['corsiva.connector'].sudo().open(connector_type='lazada')
            response_data = connector.get_order_items(action='get_order_items', lazada_order_id=lazada_order_id)
        except ValueError as e:
            return http.Response('Invalid JSON', status=400)
        self.create_order(response_data)
        return http.Response('OK', status=200)

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()
        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])

    def create_order(self, order):
        if order['code'] == '0':
            for item in order['data']:
                self.create_customer(item['buyer_id'])

        print(order)
        pass

    @staticmethod
    def create_customer(buyer_id):
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

{'data': [{'pick_up_store_info': {}, 'tax_amount': 0.0, 'reason': '', 'sla_time_stamp': '2023-12-01T23:59:59+07:00'
              , 'voucher_seller': 0, 'purchase_order_id': '', 'voucher_code_seller': '', 'voucher_code': '', 'package_id': ''
              , 'buyer_id': 200054169495, 'variation': '', 'product_id': '2494373306', 'voucher_code_platform': '', 'purchase_order_number':
               '', 'sku': 'OTO123', 'gift_wrapping': '', 'order_type': 'Normal',
           'invoice_number': '', 'cancel_return_initiator': 'null-null', 'shop_sku': '2494373306_VNAMZ-12215141846', 'is_reroute': 0,
           'stage_pay_status': '', 'sku_id': '12215141846', 'tracking_code_pre': '', 'order_item_id': 444084687469495,

           
           'shop_id': 'Nguyễn Mai Linh', 'order_flag': 'NORMAL', 'is_fbl': 0, 'name': 'Xe o to', 'delivery_option_sof': 0,
           'order_id': 444084687369495, 'fulfillment_sla': 'Bàn giao ĐVVC trước 2023-11-30 16:00:00 để được Giao Nhanh 24H_17.0 hrs_green', 'status': 'pending', 'product_main_image': 'https://sg-test-11.slatic.net/p/bb346b6e576afabfa7a3f8a77b096734.jpg', 'voucher_platform': 0, 'paid_price': 2000.0, 'product_detail_url': 'https://www.lazada.vn/products/i2494373306-s12215141846.html?urlFlag=true&mp=1', 'warehouse_code': 'dropshipping', 'promised_shipping_time': '', 'shipping_type': 'Dropshipping', 'created_at': '2023-11-29 22:23:20 +0700', 'voucher_seller_lpi': 0, 'shipping_fee_discount_platform': 0, 'personalization': '', 'wallet_credits': 0, 'updated_at': '2023-11-29 22:28:39 +0700', 'currency': 'VND', 'shipping_provider_type': 'standard', 'voucher_platform_lpi': 0, 'shipping_fee_original': 59800.0, 'item_price': 2000.0, 'is_digital': 0, 'shipping_service_cost': 0, 'tracking_code': '', 'shipping_fee_discount_seller': 0, 'shipping_amount': 59800.0, 'reason_detail': '', 'return_status': '', 'shipment_provider': 'LEX VN', 'priority_fulfillment_tag': 'POTENTIAL_NEXT_DAY,LEX_SERVICE', 'voucher_amount': 0, 'digital_delivery_info': 'minh2k3k4k@gmail.com', 'extra_attributes': ''}], 'code': '0', 'request_id': '212a68b817012735307323976'}

# Lazada
# seller
# mailinh1506@gmail.com
# Linh@123456


