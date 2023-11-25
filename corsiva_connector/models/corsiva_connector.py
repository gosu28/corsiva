import json
import requests

from odoo import api, fields, models
from odoo.addons.corsiva_connector.models import common
from odoo.exceptions import ValidationError
from datetime import datetime


SUCCESS_CODE = [200, 201]


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
            'create_access_token': '/rest/auth/token/create',
            'create_images': '/image/upload',
            'get_categories': '/category/tree/get',
            'create_products': '/product/create',
            'get_seller': '/seller/get',
            'get_products': '/products/get',
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

    def get_base_api_url(self, get_auth_url):
        return self.authorization_url if get_auth_url else self.url

    def get_common_parameters(self, action, get_access_token=False, get_language_code=False, get_auth_url=False):
        uri = self.APIs[self.connector_type][action]
        url = f"{self.get_base_api_url(get_auth_url)}{uri}"

        params = {
            "app_key": int(self.app_key),
            "timestamp": int(datetime.now().timestamp() * 1000),
            "sign_method": "sha256"
        }
        if get_access_token:
            access_token = self.env['ir.config_parameter'].sudo().get_param('lazada_access_token')
            params.update(access_token=access_token)
        if get_language_code:
            params.update(language_code=self.language_code)

        if '/rest' in uri:
            uri = uri.replace('/rest', '')

        return url, uri, params

    @staticmethod
    def get_result(response):
        if response.status_code in SUCCESS_CODE:
            json_data = json.loads(response.text)
            if json_data.get('code') == '0':
                return json_data
            if json_data.get('code') == 'IllegalAccessToken':
                raise ValidationError('The specified access token is invalid or expired. Please authorize again!')
            raise ValidationError(f"Error {json_data.get('code', '')}: {json_data.get('message', '')}")
        raise ValidationError(response.text)

    def create_access_token(self, action, code):
        url, uri, params = self.get_common_parameters(action, get_auth_url=True)
        params.update(
            code=code,
            client_secret=self.app_secret,
            grant_type="authorization_code"
        )
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.post(url=url, data=params)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)

    def create_images(self, action, data):
        url, uri, params = self.get_common_parameters(action, get_access_token=True)
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.post(url=url, params=params, files=data)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)

    def get_categories(self, action):
        url, uri, params = self.get_common_parameters(action, get_language_code=True)
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.get(url=url, params=params)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)

    def get_seller(self, action):
        url, uri, params = self.get_common_parameters(action, get_access_token=True)
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.get(url=url, params=params)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)

    def get_products(self, action):
        url, uri, params = self.get_common_parameters(action, get_access_token=True)
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.get(url=url, params=params)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)

    def create_products(self, action, data):
        url, uri, params = self.get_common_parameters(action, get_access_token=True)
        params.update(payload=json.dumps(data))
        sign = common.get_sign(self.app_secret, uri, params)
        params.update(sign=sign)

        try:
            response = requests.post(url=url, params=params)
            return self.get_result(response)
        except Exception as e:
            raise ValidationError(e.args)
