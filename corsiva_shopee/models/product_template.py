from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_shopee_product = fields.Boolean()

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('create_from_shopee', False):
            for vals in vals_list:
                vals['is_shopee_product'] = True
        return super().create(vals_list)
