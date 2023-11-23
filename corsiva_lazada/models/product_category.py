from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lazada_category_id = fields.Char()
    is_lazada = fields.Boolean()
