import hmac
import json
import time
import requests
import hashlib

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    partner_id = fields.Char()
    partner_key = fields.Char()
    redirect_url = fields.Char()
    authen_url = fields.Char()
    shopee_synced_master_data = fields.Boolean()

    @api.model
    def get_values(self):
        res = super().get_values()

        param = self.env['ir.config_parameter'].sudo()
        res.update(
            partner_id=param.get_param('shopee_partner_id'),
            partner_key=param.get_param('shopee_partner_key'),
            redirect_url=param.get_param('shopee_redirect_url'),
            authen_url=param.get_param('shopee_authen_url'),
            shopee_synced_master_data=param.get_param('shopee_synced_master_data'),
        )

        return res

    def set_values(self):
        super().set_values()

        param = self.env['ir.config_parameter'].sudo()

        field_partner_id = self.partner_id if self.partner_id else False
        field_partner_key = self.partner_key if self.partner_key else False
        field_redirect_url = self.redirect_url if self.redirect_url else False
        field_authen_url = self.authen_url if self.authen_url else False

        param.set_param('shopee_partner_id', field_partner_id)
        param.set_param('shopee_partner_key', field_partner_key)
        param.set_param('shopee_redirect_url', field_redirect_url)
        param.set_param('shopee_authen_url', field_authen_url)

    def get_sign(self, key, redirect_url):
        combined_string = key + redirect_url
        return hashlib.sha256(combined_string.encode()).hexdigest()

    def action_shopee_authorize(self):
        timestamp = int(time.time())
        path = "/api/v2/shop/auth_partner"
        partner_id = int(self.partner_id)
        partner_key = self.partner_key.encode()
        tmp_base_string = "%s%s%s" % (partner_id, path, timestamp)
        base_string = tmp_base_string.encode('utf_8')

        sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
        url = f"{self.authen_url}{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}&redirect={self.redirect_url}"
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': url
        }

    def action_shopee_synchronize_master_data(self):
        connector = self.env['shopee.connector']
        config = self.env['ir.config_parameter'].sudo()

        category_data = connector.get_category()
        if category_data:
            self.env['product.category'].create_shopee_categories(category_data['response']['category_list'])

        channel_data = connector.get_channel()
        if channel_data:
            self.env['product.logistic'].create_shopee_channel(channel_data['response']['logistics_channel_list'])

        self.shopee_synced_master_data = True
        config.set_param('shopee_synced_master_data', self.shopee_synced_master_data)
        return True
