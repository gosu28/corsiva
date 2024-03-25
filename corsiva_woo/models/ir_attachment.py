from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    lazada_product_id = fields.Many2one('product.template')

    def public_image(self):
        for res in self:
            res.public = True




