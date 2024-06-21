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
            'update_product': '/wp-json/wc/v3/products/',
            'get_category': '/wp-json/wc/v3/products/categories',
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

    def woo_update_product(self, data=None, id_woo=None):
        if self.woo_url is None:
            return ValidationError("Please connect to woo in config")
        URL_create_product = self.woo_url + self.APIs['woo']['update_product'] + id_woo
        if data is None:
            return ValidationError("No data transmitted !")
        resutl = requests.post(url=URL_create_product, json=data, auth=self._get_auth())
        if "message" in resutl:
            return ValidationError(resutl["message"])
        return self.get_result(resutl)

    def get_categories(self):
        if self.woo_url is None:
            return ValidationError("Please connect to woo in config")
        steps = 1
        while True:
            URL_create_product = (self.woo_url + self.APIs['woo']['get_category'] +
                                  "?per_page=100&page={0}".format(steps))
            response_data = requests.get(url=URL_create_product, auth=self._get_auth())
            results = self.get_result(response_data)
            if len(results) == 0:
                break
            try:
                self.env['product.category'].create_correspond_categories_woo(data=results)
            except Exception as e:
                raise ValidationError(str(e))
            steps = steps + 1



    @staticmethod
    def get_result(response):
        if response.status_code in SUCCESS_CODE:
            json_data = json.loads(response.text)
            return json_data
        raise ValidationError(response.text)







