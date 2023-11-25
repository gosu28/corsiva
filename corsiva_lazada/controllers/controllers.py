# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.addons.corsiva_connector.models import common
from odoo import http
from odoo.http import request

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

        return request.redirect('/web')

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()

        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])
