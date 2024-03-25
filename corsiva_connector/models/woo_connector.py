import json
import requests

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime
from requests.auth import HTTPBasicAuth
import requests


SUCCESS_CODE = [200, 201]


class WooConnection(models.TransientModel):
    _name = 'corsiva.woo'
    _description = 'Connector Woo'

    woo_consumer_key = fields.Char("Woo Consumer Key")
    woo_consumer_secret = fields.Char("Woo Consumer Secret")
    woo_url = fields.Char("Woo URL BASE")

    HEADERS = {
        'content-type': 'application/json'
    }

    APIs = {
        'woo': {
            'create_product': '/wp-json/wc/v3/products',
        }
    }

    @api.model
    def open(self, connector_type='woo'):
        """
        Create new connector to connect api

        @param connector_type:
        @return: connector()
        """
        connector = False
        configs = self.env['ir.config_parameter']
        if connector_type == 'woo':
            connector = self.sudo().create({
                'woo_url': configs.get_param('woo_url'),
                'woo_consumer_key': configs.get_param('woo_consumer_key'),
                'woo_consumer_secret': configs.get_param('woo_consumer_secret'),
            })
        return connector

    def _get_auth(self):
        """
        :param woo_consumer_key:
        :param woo_consumer_secret:
        :return:
            Authentication
        """
        if self.woo_consumer_key is None or self.woo_consumer_secret is None:
            return ValidationError("Please connect to woo in config")
        return HTTPBasicAuth(self.woo_consumer_key, self.woo_consumer_secret)

    def woo_create_product(self, data=None):
        if self.woo_url is None:
            return ValidationError("Please connect to woo in config")
        URL_create_product = self.woo_url + self.APIs['woo']['create_product']
        if data is None:
            return ValidationError("No data transmitted !")
        resutl = requests.post(url=URL_create_product, json=data, auth=self._get_auth())
        return self.get_result(resutl)

    @staticmethod
    def get_result(response):
        if response.status_code in SUCCESS_CODE:
            json_data = json.loads(response.text)
            return json_data
        raise ValidationError(response.text)







