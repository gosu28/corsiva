from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        if not self.is_shopee_order:
            return super().action_confirm()

        if not eval(self.env['ir.config_parameter'].sudo().get_param('corsiva_ecommerce_setup_location')):
            raise ValidationError('You need to configure the warehouse for orders from e-commerce platforms!')
        return super().action_confirm()
