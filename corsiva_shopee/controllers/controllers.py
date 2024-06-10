from odoo import http
from odoo.http import request
import json


class ShopeeControllers(http.Controller):
    @http.route('/shopee_auth', type='http', auth="none")
    def index(self, **kw):
        shop_id = kw.get('shop_id')
        code = kw.get('code')
        if shop_id and code:
            config_param = request.env['ir.config_parameter'].sudo()
            config_param.set_param('shopee_shop_id', shop_id)
            config_param.set_param('shopee_code', code)
            request.env['shopee.connector'].get_access_token()
        return request.redirect('/web')

    @http.route('/shopee_order', type='http', auth='public', csrf=False, methods=['POST'])
    def index(self, **kw):
        result = request.httprequest.data
        data = json.loads(result)
        try:
            request.env['sale.order'].sudo().create_shopee_order(data=data)
        except Exception as e:
            return http.Response(e, status=200)

        return http.Response('Success', status=200)
