from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lazada_partner = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_lazada', False):
            for vals in vals_list:
                vals['is_lazada_partner'] = True
        return super().create(vals_list)
