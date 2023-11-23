# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.addons.corsiva.corsiva_connector.models import common
from odoo import http
from odoo.http import request

import requests
import json


URL = "https://auth.lazada.com/rest/auth/token/create"


class LazadaControllers(http.Controller):

    @http.route('/lazada/', type='http', auth="none")
    def index(self, **kw):
        code = kw.get('code')
        if code:
            self.create_access_token(code)

        return request.redirect('/web')

    @staticmethod
    def create_access_token(code):
        config_param = request.env['ir.config_parameter'].sudo()

        config_param.set_param('lazada_code', code)
        client_id = config_param.get_param('lazada_app_key')
        client_secret = config_param.get_param('lazada_app_secret')
        timestamp = int(datetime.now().timestamp() * 1000)

        data = {
            "code": code,
            "app_key": client_id,
            "client_secret": client_secret,
            "sign_method": "sha256",
            "grant_type": "authorization_code",
            "timestamp": timestamp
        }
        sign = common.get_sign(client_secret, '/auth/token/create', data)
        data.update(sign=sign)

        response = requests.post(URL, data=data)
        json_data = json.loads(response.text)

        config_param.set_param('lazada_access_token', json_data['access_token'])
        config_param.set_param('lazada_refresh_token', json_data['refresh_token'])
