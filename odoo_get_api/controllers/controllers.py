from odoo import http
from odoo.http import request
import json
from odoo.exceptions import AccessError


class OdooApi(http.Controller):
    @http.route('/login-app', type='http', auth='public', csrf=False, methods=['GET', 'POST'], cors="*")
    def login_app(self, login, password,  **kw):
        # result = request.httprequest.data
        # data = json.loads(result)
        # login = data.get('login')
        # password = data.get('password')
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
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})

    @http.route('/logout-app', type='http', auth='public', csrf=False, methods=['GET', 'POST'], cors="*")
    def logout_app(self, login, password, **kw):
        # result = request.httprequest.data
        # data = json.loads(result)
        # login = data.get('login')
        # password = data.get('password')

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
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})

    @http.route('/get-list-order', type='http', auth='public', csrf=False, methods=['GET'], cors="*")
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
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})

    @http.route('/get-detail-order', type='http', auth='public', csrf=False, methods=['GET', 'POST'], cors="*")
    def get_detail_order(self, login, password, name, **kw):
        try:
            # result = request.httprequest.data
            # data = json.loads(result)
            # so_name = data.get('name')
            order = request.env['sale.order'].sudo().search([('name', '=', name)], limit=1)
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
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})

    @http.route('/get-list-product', type='http', auth='public', csrf=False, methods=['GET', 'POST'], cors="*")
    def get_list_product(self, **kw):
        try:
            result = request.httprequest.data
            data = json.loads(result)
            product_list = []
            product_ids = request.env['product.template'].sudo().search([])
            url_base = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            for product_id in product_ids:
                product_dict = {
                    'name': product_id.name,
                    'code': product_id.default_code,
                    'price': product_id.list_price,
                    'image': '{0}/web/image/product.template/{1}/image_1920'.format(url_base, product_id.id),
                    'quantity': product_id.qty_available,
                }
                product_list.append(product_dict)

            result = {
                'data': product_list,
                'status': 200,
                'msg': 'Load data Successful',
            }
        except AccessError as e:
            result = {
                'data': [],
                'status': 400,
                'msg': 'Load data Fail',
            }
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})

    @http.route('/get-detail-user', type='http', auth='public', csrf=False, methods=['GET', 'POST'], cors="*")
    def get_detail_user(self, login, password, **kw):
        try:
            # result = request.httprequest.data
            # data = json.loads(result)
            # login = data.get('login')
            # password = data.get('password')
            login = request.env['login.app'].sudo().search([('login', '=', login),
                                                            ('password', '=', password)], limit=1)

            result = {
                'data': {
                    'name': login.name,
                    'phone': login.phone
                },
                'status': 200,
                'msg': 'Load data Successful',
            }
        except Exception as e:
            result = {
                'data': {},
                'status': 400,
                'msg': 'Load data Fail',
            }
        return http.Response(json.dumps(result), headers={'Content-Type': 'application/json'})


