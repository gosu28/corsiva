from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    buyer_user_id = fields.Char()
