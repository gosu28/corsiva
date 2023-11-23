from odoo import api, fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    lazada_product_id = fields.Many2one('product.template')
    public_url = fields.Char(compute='_compute_public_url', store=True)

    @api.depends('local_url')
    def _compute_public_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for r in self:
            if not r.local_url:
                r.public_url = False
                continue

            r.public_url = f"{base_url}{r.local_url.split('?')[0]}"
