from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _name = 'corsiva.ecommerce'

    name = fields.Char(String="Name")
    description = fields.Char(String="Description")
