from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    short_description = fields.Html(
        string='Description'
    )
    image_ids = fields.Many2many(
        'ir.attachment',
        'product_template_ir_attachment_rel',
        string='Upload Images'
    )
    image_kanban_ids = fields.Many2many(
        'ir.attachment',
        'product_template_kanban_ir_attachment_rel',
        compute='_compute_image_kanban_ids',
        inverse='_inverse_image_kanban_ids',
        ondelete='cascade',
        store=True
    )

    @api.depends('image_ids')
    def _compute_image_kanban_ids(self):
        for r in self:
            r.image_kanban_ids = r.image_ids.ids

    def _inverse_image_kanban_ids(self):
        for r in self:
            r.image_ids = r.image_kanban_ids.ids

