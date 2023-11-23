import json
from datetime import datetime

import requests

from odoo import api, fields, models
from odoo.addons.corsiva.corsiva_connector.models import common

from odoo.exceptions import ValidationError

SUCCESS = [200, 201]


class CorsivaConnector(models.TransientModel):
    _name = 'corsiva.connector'
    _description = 'Connector'

    url = fields.Char()
    app_key = fields.Char()
    app_secret = fields.Char()
    callback_url = fields.Char()
    authorization_url = fields.Char()
    language_code = fields.Char()
    country = fields.Char()
    connector_type = fields.Char()

    HEADERS = {
        'content-type': 'application/json'
    }

    APIs = {
        'lazada': {
            'create_images': '/image/upload',
            'get_categories': '/category/tree/get'
        }
    }

    @api.model
    def open(self, connector_type=False):
        """
        Create new connector to connect api

        @param connector_type:
        @return: connector()
        """
        connector = False
        configs = self.env['ir.config_parameter']
        if connector_type == 'lazada':
            connector = self.sudo().create({
                'url': configs.get_param('lazada_url'),
                'app_key': configs.get_param('lazada_app_key'),
                'app_secret': configs.get_param('lazada_app_secret'),
                'callback_url': configs.get_param('lazada_callback_url'),
                'authorization_url': configs.get_param('lazada_authorization_url'),
                'language_code': configs.get_param('lazada_language_code'),
                'country': configs.get_param('lazada_country'),
                'connector_type': connector_type
            })
        return connector

    def get_base_api_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('lazada_url')

    def create_images(self, action, raw_data):
        uri = self.APIs[self.connector_type][action]
        url = self.get_base_api_url()
        config_param = self.env['ir.config_parameter'].sudo()

        app_key = config_param.get_param('lazada_app_key')
        app_secret = config_param.get_param('lazada_app_secret')
        access_token = config_param.get_param('lazada_access_token')
        timestamp = int(datetime.now().timestamp() * 1000)

        params = {
            "app_key": app_key,
            "timestamp": timestamp,
            "access_token": access_token,
            "sign_method": "sha256"
        }
        files = {
            "image": open(raw_data._full_path(raw_data.store_fname), 'rb').read()
        }
        sign = common.get_sign(app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.post(url=f"{url}{uri}", params=params, files=files)
            if response.status_code in SUCCESS:
                json_data = json.loads(response.text)
                return json_data
        except Exception as e:
            raise ValidationError(e.args)

    def get_categories(self, action):
        uri = self.APIs[self.connector_type][action]
        url = self.get_base_api_url()
        config_param = self.env['ir.config_parameter'].sudo()

        app_key = config_param.get_param('lazada_app_key')
        app_secret = config_param.get_param('lazada_app_secret')
        language_code = config_param.get_param('lazada_language_code')
        access_token = config_param.get_param('lazada_access_token')
        timestamp = int(datetime.now().timestamp() * 1000)

        data = {
            "app_key": app_key,
            "timestamp": timestamp,
            # "access_token": access_token,
            "sign_method": "sha256",
            "language_code": language_code
        }

        sign = common.get_sign(app_secret, uri, data)
        data.update(sign=sign)

        try:
            response = requests.get(url=f"{url}{uri}", params=data)
            if response.status_code in SUCCESS:
                json_data = json.loads(response.text)
                return json_data
        except Exception as e:
            raise ValidationError(e.args)
