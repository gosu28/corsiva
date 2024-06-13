from odoo import api, fields, models


class LoginApp(models.Model):
    _name = 'login.app'

    login = fields.Char(string='Login', required=True)
    password = fields.Char(string='Password', required=True)
    name = fields.Char(string='Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    active_on = fields.Boolean(string='Active', default=False)

    def get_data(self):
        self.ensure_one()
        self.active_on = True
        data = {
            'data': {
                'login': self.login,
                'password': self.password,
                'active_on': self.active_on
            },
            'status': 200,
            'msg': 'Login Successful',
        }
        return data

    def logout_api(self):
        self.ensure_one()
        self.active_on = False
