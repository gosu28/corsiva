from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    woo_consumer_key = fields.Char("Woo Consumer Key", related="company_id.woo_consumer_key", readonly=False)
    woo_consumer_secret = fields.Char("Woo Consumer Secret", related="company_id.woo_consumer_secret", readonly=False)
    woo_url = fields.Char("Woo URL BASE", related="company_id.woo_url", readonly=False)

    @api.model
    def get_values(self):
        res = super().get_values()

        param = self.env['ir.config_parameter'].sudo()
        res.update(
            woo_consumer_key=param.get_param('woo_consumer_key'),
            woo_consumer_secret=param.get_param('woo_consumer_secret'),
            woo_url=param.get_param('woo_url'),
        )

        return res

    def set_values(self):
        super().set_values()

        param = self.env['ir.config_parameter'].sudo()

        field_woo_url = self.woo_url if self.woo_url else False
        field_woo_consumer_key = self.woo_consumer_key if self.woo_consumer_key else False
        field_woo_consumer_secret = self.woo_consumer_secret if self.woo_consumer_secret else False

        param.set_param('woo_url', field_woo_url)
        param.set_param('woo_consumer_key', field_woo_consumer_key)
        param.set_param('woo_consumer_secret', field_woo_consumer_secret)
