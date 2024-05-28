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

    def get_access_token(self):
        code = self.env['ir.config_parameter'].sudo().get_param('shopee_code')
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s" % (partner_id, get_access_token, timestamp), tmp_partner_key)

        url = f"{url}{get_access_token}?partner_id={partner_id}&sign={sign}&timestamp={timestamp}"
        body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
        headers = {"Content-Type": "application/json"}

        resp = requests.post(url, json=body, headers=headers)
        ret = json.loads(resp.content)

        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('shopee_access_token', ret.get("access_token"))
        config_param.set_param('shopee_refresh_token', ret.get("refresh_token"))
        return True

    def refresh_token(self):
        refresh_token = self.env['ir.config_parameter'].sudo().get_param('shopee_refresh_token')
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s" % (partner_id, refresh_access_token, timestamp), tmp_partner_key)

        url = f"{url}{refresh_access_token}?partner_id={partner_id}&sign={sign}&timestamp={timestamp}"
        body = {"refresh_token": refresh_token, "shop_id": shop_id, "partner_id": partner_id}
        headers = {"Content-Type": "application/json"}

        resp = requests.post(url, json=body, headers=headers)
        ret = json.loads(resp.content)

        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('shopee_access_token', ret.get("access_token"))
        config_param.set_param('shopee_refresh_token', ret.get("refresh_token"))
        return True

    def post_images(self, data):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s" % (partner_id, post_image, timestamp), tmp_partner_key)
        url = f"{url}{post_image}?partner_id={partner_id}&sign={sign}&timestamp={timestamp}"
        response = requests.request("POST", url, headers={}, files=data)

        if response.status_code not in SUCCESS:
            raise ValidationError(json.loads(response.text)['message'])
        if response.status_code in SUCCESS:
            if json.loads(response.text).get('message') not in ('', False):
                raise ValidationError(json.loads(response.text).get('message'))

        return json.loads(response.text)

    @staticmethod
    def call(url, headers, payload, method):
        response = requests.request(method, url, headers=headers, data=payload)

        if response.status_code not in SUCCESS:
            raise ValidationError(json.loads(response.text)['message'])
        if response.status_code in SUCCESS:
            if json.loads(response.text).get('debug_message') not in ('', False):
                raise ValidationError(json.loads(response.text).get('debug_message'))
            if json.loads(response.text).get('message') not in ('', False):
                raise ValidationError(json.loads(response.text).get('message'))

        return json.loads(response.text)

    def get_category(self):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, get_category, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{get_category}?access_token={access_token}&language=zh-hans&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        return self.call(url, headers={}, payload={}, method='GET')

    def get_channel(self):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, get_channel, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{get_channel}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        return self.call(url, headers={}, payload={}, method='GET')

    def post_products(self, data):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, post_product, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{post_product}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        return self.call(url, headers=headers, payload=payload, method='POST')

    def update_products(self, data):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, update_product, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{update_product}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        return self.call(url, headers=headers, payload=payload, method='POST')

    def update_stock(self, data):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, update_stock, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{update_stock}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        return self.call(url, headers=headers, payload=payload, method='POST')

    def update_price(self, data):
        access_token, url, timestamp, partner_id, tmp_partner_key, shop_id = self.get_shopee_config()
        sign = self.get_sign("%s%s%s%s%s" % (partner_id, update_price, timestamp, access_token, shop_id), tmp_partner_key)
        url = f"{url}{update_price}?access_token={access_token}&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timestamp}"
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        return self.call(url, headers=headers, payload=payload, method='POST')
