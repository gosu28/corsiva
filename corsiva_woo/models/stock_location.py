from odoo import api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    woo_stock = fields.Boolean()
