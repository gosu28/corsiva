from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    short_description = fields.Html(
        string='Description'
    )

