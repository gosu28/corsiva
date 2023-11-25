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

        action_id = request.env['ir.actions.actions'].sudo().search([('name', '=', 'Lazada Settings')]).id
        menu_id = request.env['ir.ui.menu'].sudo().search([('name', '=', 'Lazada')]).id
        if action_id and menu_id:
            url = '/web?db=%s#action=%s&model=res.config.settings&view_type=form&cids=1&menu_id=%s' % (request.env.cr.dbname, action_id, menu_id)
        else:
            url = '/web'

        return request.redirect(url)

    @staticmethod
    def save_auth_data(data):
        config_param = request.env['ir.config_parameter'].sudo()

        config_param.set_param('lazada_access_token', data['access_token'])
        config_param.set_param('lazada_refresh_token', data['refresh_token'])
        config_param.set_param('lazada_expires_in', data['expires_in'])
        config_param.set_param('lazada_refresh_expires_in', data['refresh_expires_in'])
