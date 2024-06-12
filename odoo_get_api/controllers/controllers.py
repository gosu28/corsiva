from odoo import http
from odoo.http import request
import json
from odoo.exceptions import AccessError


class OdooApi(http.Controller):
    @http.route('/login-app', type='json', auth='public', csrf=False, methods=['POST'])
    def login_app(self, **kw):
        result = request.httprequest.data
        data = json.loads(result)
        login = data.get('login')
        password = data.get('password')
        login = request.env['login.app'].sudo().search([('login', '=', login),
                                                        ('password', '=', password)], limit=1)
        if login:
            result = login.get_data()
        else:
            result = {
                'data': {},
                'status': 400,
                'msg': 'Login Fail',
            }
        return result

    @http.route('/logout-app', type='json', auth='public', csrf=False, methods=['POST'])
    def logout_app(self, **kw):
        result = request.httprequest.data
        data = json.loads(result)
        login = data.get('login')
        password = data.get('password')

        login = request.env['login.app'].sudo().search([('login', '=', login),
                                                        ('password', '=', password)], limit=1)
        if login:
            login.logout_api()
            result = {
                'data': {},
                'status': 200,
                'msg': 'Logout Successful',
            }
        else:
            result = {
                'data': {},
                'status': 400,
                'msg': 'Logout Fail',
            }
        return result

    @http.route('/get-list-order', type='json', auth='public', csrf=False, methods=['GET'])
    def list_order(self, **kw):
        try:
            order = request.env['sale.order'].sudo().search([])
            data = []
            for rec in order:
                order_dict = {
                    'name': rec.name,
                    'customer': rec.partner_id.name,
                    'phone': rec.partner_id.phone,
                    'total': rec.amount_total,
                    'state': rec.state
                }
                data.append(order_dict)

            result = {
                'data': data,
                'status': 200,
                'msg': 'Load data Successful',
            }
        except AccessError as e:
            result = {
                'data': [],
                'status': 400,
                'msg': 'Load data Fail',
            }
        return result

    @http.route('/get-detail-order', type='json', auth='public', csrf=False, methods=['POST'])
    def get_detail_order(self, **kw):
        try:
            result = request.httprequest.data
            data = json.loads(result)
            so_name = data.get('name')
            order = request.env['sale.order'].sudo().search([('name', '=', so_name)], limit=1)
            order_dict = {
                'name': order.name,
                'customer': order.partner_id.name,
                'phone': order.partner_id.phone,
                'total': order.amount_total,
                'state': order.state,
                'salesperson': order.user_id.name,
                'sale_phone': order.user_id.phone,
                'order_line': []
            }
            for line in order.order_line:
                lines = {
                    'name': line.product_id.name,
                    'quantity': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                }
                order_dict['order_line'].append(lines)

            result = {
                'data': order_dict,
                'status': 200,
                'msg': 'Load data Successful',
            }
        except AccessError as e:
            result = {
                'data': [],
                'status': 400,
                'msg': 'Load data Fail',
            }
        return result

