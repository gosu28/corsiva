from odoo import api, fields, models
from datetime import datetime
import requests
import json
import time
import hashlib
import hmac

from odoo.exceptions import ValidationError

SUCCESS = [200, 201]

get_category = '/api/v2/product/get_category'
get_access_token = '/api/v2/auth/token/get'


class ShopeeConnectorAPI(models.TransientModel):
    _name = 'shopee.connector'

    def get_sign(self, tmp_base_string, tmp_partner_key):
        base_string = tmp_base_string.encode()
        partner_key = tmp_partner_key.encode()
        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        return sign

    def get_access_token(self):
        code = self.env['ir.config_parameter'].sudo().get_param('shopee_code')
        partner_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_partner_id'))
        tmp_partner_key = self.env['ir.config_parameter'].sudo().get_param('shopee_partner_key')
        shop_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_shop_id'))

        timest = int(time.time())
        host = "https://partner.test-stable.shopeemobile.com"
        path = "/api/v2/auth/token/get"
        body = {"code": code, "shop_id": shop_id, "partner_id": partner_id}
        sign = self.get_sign("%s%s%s" % (partner_id, path, timest), tmp_partner_key)
        url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timest, sign)
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=body, headers=headers)
        ret = json.loads(resp.content)
        config_param = self.env['ir.config_parameter'].sudo()
        config_param.set_param('shopee_access_token', ret.get("access_token"))
        config_param.set_param('shopee_refresh_token', ret.get("refresh_token"))
        # return ret.get("access_token")
        return True

    def call(self):
        access_token = self.env['ir.config_parameter'].sudo().get_param('shopee_access_token')
        url = 'https://partner.test-stable.shopeemobile.com'
        timest = int(time.time())
        partner_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_partner_id'))
        tmp_partner_key = self.env['ir.config_parameter'].sudo().get_param('shopee_partner_key')
        shop_id = int(self.env['ir.config_parameter'].sudo().get_param('shopee_shop_id'))

        sign = self.get_sign("%s%s%s%s%s" % (partner_id, get_category, timest, access_token, shop_id), tmp_partner_key)
        url = f"{url}{get_category}?access_token={access_token}&language=zh-hans&partner_id={partner_id}&shop_id={shop_id}&sign={sign}&timestamp={timest}"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        if response.status_code not in SUCCESS:
            raise ValidationError(json.loads(response.text)['message'])

        data = json.loads(response.text)
        return data

