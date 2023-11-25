from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    app_key = fields.Char()
    app_secret = fields.Char()
    url = fields.Char(string="API URL")
    callback_url = fields.Char()
    authorization_url = fields.Char()
    language_code = fields.Selection(string='Language Code', default='en_US',
                                     selection=[('en_US', 'English'), ('en_SG', 'Singapore'), ('th_TH', 'Thailand'),
                                                ('id_ID', 'Indonesia'), ('vi_VN', 'Vietnam'), ('fil_PH', 'Philippines'),
                                                ('ms_MY', 'Malaysia')])
    country = fields.Selection(string='Region', default='vn',
                               selection=[('vn', 'Vietnam'), ('sg', 'Singapore'), ('ph', 'Philippines'),
                                          ('my', 'Malaysia'), ('th', 'Thailand'), ('id', 'Indonesia')])
    synced_product_category = fields.Boolean()
    synced_brand = fields.Boolean()

    @api.onchange('country')
    def _onchange_country(self):
        if self.country == 'vn':
            self.url = 'https://api.lazada.vn/rest'
        elif self.country == 'sg':
            self.url = 'https://api.lazada.sg/rest'
        elif self.country == 'ph':
            self.url = 'https://api.lazada.com.ph/rest'
        elif self.country == 'my':
            self.url = 'https://api.lazada.com.my/rest'
        elif self.country == 'th':
            self.url = 'https://api.lazada.co.th/rest'
        elif self.country == 'id':
            self.url = 'https://api.lazada.co.id/rest'
        else:
            self.url = False

    @api.model
    def get_values(self):
        res = super().get_values()

        param = self.env['ir.config_parameter'].sudo()
        res.update(
            app_key=param.get_param('lazada_app_key'),
            app_secret=param.get_param('lazada_app_secret'),
            url=param.get_param('lazada_url'),
            callback_url=param.get_param('lazada_callback_url'),
            authorization_url=param.get_param('lazada_authorization_url'),
            language_code=param.get_param('lazada_language_code'),
            country=param.get_param('lazada_country'),
            synced_product_category=param.get_param('lazada_synced_product_category'),
            synced_brand=param.get_param('lazada_synced_brand'),
        )

        return res

    def set_values(self):
        super().set_values()

        param = self.env['ir.config_parameter'].sudo()

        field_app_key = self.app_key if self.app_key else False
        field_app_secret = self.app_secret if self.app_secret else False
        field_url = self.url if self.url else False
        field_callback_url = self.callback_url if self.callback_url else False
        field_authorization_url = self.authorization_url if self.authorization_url else False
        field_language_code = self.language_code if self.language_code else False
        field_country = self.country if self.country else False

        param.set_param('lazada_app_key', field_app_key)
        param.set_param('lazada_app_secret', field_app_secret)
        param.set_param('lazada_url', field_url)
        param.set_param('lazada_callback_url', field_callback_url)
        param.set_param('lazada_authorization_url', field_authorization_url)
        param.set_param('lazada_language_code', field_language_code)
        param.set_param('lazada_country', field_country)

    def action_authorize(self):
        data = {
            'response_type': 'code',
            'redirect_uri': self.callback_url,
            'client_id': self.app_key,
            'force_auth': True
        }

        auth_url = self.authorization_url + '/oauth/authorize'
        authorization_redirect_url = auth_url + "?" + "&".join([f"{key}={value}" for key, value in data.items()])

        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': authorization_redirect_url
        }

    def action_synchronize_product_category(self):
        self.synced_product_category = True
        self.env['ir.config_parameter'].sudo().set_param('lazada_synced_product_category', self.synced_product_category)

        connector = self.env['corsiva.connector'].open(connector_type='lazada')
        category_data = connector.get_categories(action='get_categories')
        return self.env['product.category'].create_correspond_categories(category_data['data'])
