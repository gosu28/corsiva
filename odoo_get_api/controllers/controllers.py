from odoo import http
from odoo.http import request
import json


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
    def login_app(self, **kw):
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

    @http.route('/get-order-app', type='json', auth='public', csrf=False, methods=['POST'])
    def login_app(self, **kw):
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

