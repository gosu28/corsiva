from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    url = fields.Char()
    username = fields.Char()
    password = fields.Char()

    @api.model
    def get_values(self):
        res = super().get_values()

        param = self.env['ir.config_parameter'].sudo()
        res.update(
            url=param.get_param('shopee_url'),
            username=param.get_param('shopee_username'),
            password=param.get_param('shopee_password')
        )

        return res

    def set_values(self):
        super().set_values()

        param = self.env['ir.config_parameter'].sudo()

        field_url = self.url if self.url else False
        field_username = self.username if self.username else False
        field_password = self.password if self.password else False

        param.set_param('shopee_url', field_url)
        param.set_param('shopee_username', field_username)
        param.set_param('shopee_password', field_password)
