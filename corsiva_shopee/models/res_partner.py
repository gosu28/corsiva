from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_shopee_partner = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_shopee', False):
            for vals in vals_list:
                vals['is_shopee_partner'] = True
        return super().create(vals_list)
