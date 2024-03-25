from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description = fields.Text(
        string='Description'
    )
    short_description = fields.Text(
        string='Short Description'
    )