from odoo import api, fields, models
from datetime import datetime
import requests
import json
import time
import hashlib
import hmac

from odoo.exceptions import ValidationError

SUCCESS = [200, 201]

get_access_token = '/api/v2/auth/token/get'
refresh_access_token = '/api/v2/auth/access_token/get'
get_category = '/api/v2/product/get_category'
get_channel = '/api/v2/logistics/get_channel_list'
post_image = '/api/v2/media_space/upload_image'
post_product = '/api/v2/product/add_item'
update_product = '/api/v2/product/update_item'
update_stock = '/api/v2/product/update_stock'
update_price = '/api/v2/product/update_price'


class ShopeeConnectorAPI(models.TransientModel):
    _name = 'shopee.connector'

    def get_sign(self, tmp_base_string, tmp_partner_key):
        base_string = tmp_base_string.encode()
        partner_key = tmp_partner_key.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        return sign

    def get_shopee_config(self):
        access_token = self.env['ir.config_parameter'].sudo().get_param('shopee_access_token')
        url = 'https://partner.test-stable.shopeemobile.com'
        timestamp = int(time.time())
        partner_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_partner_id'))
        tmp_partner_key = self.env['ir.config_parameter'].sudo().get_param('shopee_partner_key')
        shop_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_shop_id'))
        return access_token, url, timestamp, partner_id, tmp_partner_key, shop_id

    def action_get_token(self, key, body):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s" % (partner_id, key, timestamp), tmp_partner_key)

        url = f"{url}{key}?partner_id={partner_id}&sign={sign}&timestamp={timestamp}"
        headers = {"Content-Type": "application/json"}
        body.update(shop_id=shop_id, partner_id=partner_id)

        response = requests.post(url, json=body, headers=headers)
        result = json.loads(response.content)

        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('shopee_access_token', result.get("access_token"))
        config_param.set_param('shopee_refresh_token', result.get("refresh_token"))
        return True

    def call(self, key, headers, payload, method, upload_file=False):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, key, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{key}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"

        if upload_file:
            response = requests.request("POST", url, headers={}, files=payload)
        else:
            response = requests.request(method, url, headers=headers, data=payload)

        if response.status_code not in SUCCESS:
            raise ValidationError(json.loads(response.text)['message'])

        if response.status_code in SUCCESS:
            if json.loads(response.text).get('message') not in ('', False):
                raise ValidationError(json.loads(response.text).get('message'))

        return json.loads(response.text)

    def action_get(self, key):
        return self.call(key, headers={}, payload={}, method='GET')

    def action_post(self, payload, key, upload_file=False):
        headers = {'Content-Type': 'application/json'}
        if not upload_file:
            payload = json.dumps(payload)
        return self.call(key, headers=headers, payload=payload, method='POST', upload_file=upload_file)

    def get_access_token(self):
        code = self.env['ir.config_parameter'].sudo().get_param('shopee_code')
        return self.action_get_token(get_access_token, body={"code": code})

    def refresh_token(self):
        refresh_token = self.env['ir.config_parameter'].sudo().get_param('shopee_refresh_token')
        return self.action_get_token(refresh_access_token, body={"refresh_token": refresh_token})

    def get_category(self):
        return self.action_get(key=get_category)

    def get_channel(self):
        return self.action_get(key=get_channel)

    def post_products(self, data):
        return self.action_post(payload=data, key=post_product)

    def post_images(self, data):
        return self.action_post(payload=data, key=post_image, upload_file=True)

    def update_products(self, data):
        return self.action_post(payload=data, key=update_product)

    def update_stock(self, data):
        return self.action_post(payload=data, key=update_stock)

    def update_price(self, data):
        return self.action_post(payload=data, key=update_price)
