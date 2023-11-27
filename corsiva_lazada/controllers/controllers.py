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
        # Xác minh tính hợp lệ của thông điệp nếu cần
        # Lazada thường cung cấp các thông điệp được ký số để xác minh nguồn gốc

        # Xử lý dữ liệu JSON từ Lazada
        try:
            data = json.loads(request.httprequest.data)
            lazada_order_id = data['data']['trade_order_id']
            connector = request.env['corsiva.connector'].sudo().open(connector_type='lazada')
            response_data = connector.get_order(action='get_order', lazada_order_id=lazada_order_id)
            self.create_order(response_data)
        except ValueError as e:
            return http.Response('Invalid JSON', status=400)

        # Xử lý thông điệp từ Lazada ở đây
        # ...

        # Phản hồi 200 OK để Lazada biết rằng thông điệp đã được nhận thành công
        return http.Response('OK', status=200)

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()

        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])

        # data = {'seller_id': '200549968600', 'message_type': 0,
        #         'data': {'order_status': 'pending', 'trade_order_id': '446156718969495',
        #                  'trade_order_line_id': '446156719069495', 'status_update_time': 1701074452,
        #                  'buyer_id': '200054169495'}, 'timestamp': 1701074463, 'site': 'lazada_vn'}
        # data = {'seller_id': '200549968600', 'message_type': 0,
        #         'data': {'order_status': 'unpaid', 'trade_order_id': '446156718969495',
        #                  'trade_order_line_id': '446156719069495', 'status_update_time': 1701074452,
        #                  'buyer_id': '200054169495'}, 'timestamp': 1701074462, 'site': 'lazada_vn'}

    # def sreach_order_lazada(self, order_id):
    #
    #     pass
    #
    def create_order(self, order):
        print(order)
        # {'voucher': 0.0, 'warehouse_code': 'dropshipping', 'order_number': 446156718969495,
        #  'created_at': '2023-11-27 15:40:52 +0700', 'voucher_code': '', 'gift_option': False,
        #  'shipping_fee_discount_platform': 0.0, 'customer_last_name': '', 'updated_at': '2023-11-27 16:27:04 +0700',
        #  'promised_shipping_times': '', 'price': '2000.00', 'national_registration_number': '',
        #  'shipping_fee_original': 59800.0, 'payment_method': 'COD', 'buyer_note': '',
        #  'customer_first_name': 'M***********V', 'shipping_fee_discount_seller': 0.0, 'shipping_fee': 59800.0,
        #  'branch_number': '', 'tax_code': '', 'items_count': 1, 'delivery_info': '', 'statuses': ['canceled'],
        #  'address_billing': {'country': 'Vietnam', 'address3': 'H****i', 'address2': '', 'city': 'Quận Hà Đông',
        #                      'phone': '84********36', 'address1': 's**********2', 'post_code': '', 'phone2': '',
        #                      'last_name': '', 'address5': 'H*********************************o',
        #                      'address4': 'Q**********g', 'first_name': 'n*************h'},
        #  'extra_attributes': '{"TaxInvoiceRequested":false}', 'order_id': 446156718969495, 'gift_message': '',
        #  'remarks': '',
        #  'address_shipping': {'country': 'Vietnam', 'address3': 'H****i', 'address2': '', 'city': 'Quận Hà Đông',
        #                       'phone': '84********36', 'address1': 's**********2', 'post_code': '', 'phone2': '',
        #                       'last_name': '', 'address5': 'P***********o', 'address4': 'Q**********g',
        #                       'first_name': 'n*************h'}}

        {'data': {'voucher': 0.0, 'warehouse_code': 'dropshipping', 'order_number': 443701418369495,
                  'created_at': '2023-11-27 17:18:12 +0700', 'voucher_code': '', 'gift_option': False,
                  'shipping_fee_discount_platform': 0.0, 'customer_last_name': '',
                  'updated_at': '2023-11-27 17:18:14 +0700', 'promised_shipping_times': '', 'price': '25000.00',
                  'national_registration_number': '', 'shipping_fee_original': 16000.0, 'payment_method': 'COD',
                  'buyer_note': '', 'customer_first_name': 'M***********V', 'shipping_fee_discount_seller': 0.0,
                  'shipping_fee': 16000.0, 'branch_number': '', 'tax_code': '', 'items_count': 1, 'delivery_info': '',
                  'statuses': ['pending'],
                  'address_billing': {'country': 'Vietnam', 'address3': 'H****i', 'address2': '',
                                      'city': 'Quận Hà Đông', 'phone': '84********36', 'address1': 's**********2',
                                      'post_code': '', 'phone2': '', 'last_name': '',
                                      'address5': 'H*********************************o', 'address4': 'Q**********g',
                                      'first_name': 'n*************h'},
                  'extra_attributes': '{"TaxInvoiceRequested":false}', 'order_id': 443701418369495, 'gift_message': '',
                  'remarks': '', 'address_shipping': {'country': 'Vietnam', 'address3': 'H****i', 'address2': '',
                                                      'city': 'Quận Hà Đông', 'phone': '84********36',
                                                      'address1': 's**********2', 'post_code': '', 'phone2': '',
                                                      'last_name': '', 'address5': 'P***********o',
                                                      'address4': 'Q**********g', 'first_name': 'n*************h'}},
         'code': '0', 'request_id': '2101430e17010803032811460'}

        pass


