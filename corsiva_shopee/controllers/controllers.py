from odoo import http
from odoo.http import request


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
