import json
import requests

from odoo import api, fields, models

SUCCESS = [200, 201]


class CorsivaConnector(models.AbstractModel):
    _name = 'corsiva.connector'
    _description = 'Connector'

    api_url = fields.Char()
    username = fields.Char()
    password = fields.Char()

    HEADERS = {
        'content-type': 'application/json'
    }

    APIs = {
        'auth': 'auth',
        'order_create': 'order/create',
        'order_status': 'order/status',
    }

    @api.model
    def open(self):
        """
        Create new connector to connect api
        @return:
        """
        configs = self.env['ir.config_parameter']
        connector = self.create({
            'api_url': configs.get('api_url'),
            'username': configs.get('api_username'),
            'password': configs.get('api_password')
        })

        api_token = self._get_api_token()
        if api_token:
            connector.api_token = api_token
            return connector

        return False

    def _get_api_token(self):
        """

        @return:
        """
        data = {'username': self.username, 'password': self.password}
        try:
            response = requests.get(url=self.api_url, headers=self.HEADERS, data=data)
            if response.status_code in SUCCESS:
                return json.loads(response)['api_token']
            return False
        except Exception as e:
            return False
