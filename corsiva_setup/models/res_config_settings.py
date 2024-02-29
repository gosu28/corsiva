from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    location_setting = fields.Selection(string='Location Setting',
                                        selection=[
                                            ('shared_location', 'Shared Storage'),
                                            ('separate_location', 'Use a Separate Storage'),
                                            ('shopee_n_lazada', 'Shopee & Lazada Utilize a Shared Storage'),
                                            ('shopee_n_woo', 'Shopee & Woo Utilize a Shared Storage'),
                                            ('woo_n_lazada', 'Lazada & Woo Utilize a Shared Storage'),
                                        ], default='shared_location')
    ecommerce_setup_location = fields.Boolean(string='Setup E-commerce Location')
    setup_once_time = fields.Boolean()

    @api.model
    def get_values(self):
        res = super().get_values()

        param = self.env['ir.config_parameter'].sudo()
        res.update(
            location_setting=param.get_param('corsiva_location_setting'),
            ecommerce_setup_location=param.get_param('corsiva_ecommerce_setup_location'),
            setup_once_time=param.get_param('setup_once_time'),
        )

        return res

    def set_values(self):
        super().set_values()

        lazada_stock_id = shopee_stock_id = woo_stock_id = False
        param = self.env['ir.config_parameter'].sudo()

        field_ecommerce_setup_location = self.ecommerce_setup_location if self.ecommerce_setup_location else False
        field_location_setting = self.location_setting if self.location_setting else False

        if field_ecommerce_setup_location:
            if self.location_setting == 'shared_location':
                lazada_stock_id = shopee_stock_id = woo_stock_id = self.env.ref('corsiva_setup.ecommerce_location').id
            elif self.location_setting == 'separate_location':
                lazada_stock_id = self.env.ref('corsiva_setup.lazada_stock_location').id
                shopee_stock_id = self.env.ref('corsiva_setup.shopee_stock_location').id
                woo_stock_id = self.env.ref('corsiva_setup.woo_stock_location').id
            elif self.location_setting == 'shopee_n_lazada':
                shopee_stock_id = lazada_stock_id = self.env.ref('corsiva_setup.shopee_n_lazada_location').id
                woo_stock_id = self.env.ref('corsiva_setup.woo_stock_location').id
            elif self.location_setting == 'shopee_n_woo':
                shopee_stock_id = woo_stock_id = self.env.ref('corsiva_setup.shopee_n_woo_location').id
                lazada_stock_id = self.env.ref('corsiva_setup.lazada_stock_location').id
            elif self.location_setting == 'woo_n_lazada':
                woo_stock_id = lazada_stock_id = self.env.ref('corsiva_setup.woo_n_lazada_location').id
                shopee_stock_id = self.env.ref('corsiva_setup.shopee_stock_location').id

        param.set_param('corsiva_ecommerce_setup_location', field_ecommerce_setup_location)
        param.set_param('corsiva_location_setting', field_location_setting)
        param.set_param('lazada_stock', lazada_stock_id)
        param.set_param('shopee_stock', shopee_stock_id)
        param.set_param('woo_stock', woo_stock_id)
        param.set_param('setup_once_time', True)
