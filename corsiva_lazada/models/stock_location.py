from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    lazada_stock = fields.Boolean()
