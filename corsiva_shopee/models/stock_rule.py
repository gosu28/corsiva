from odoo import api, fields, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        res = super()._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values)
        if origin:
            so_id = self.env['sale.order'].search([('name', '=', origin)], limit=1)
            if so_id and so_id.is_shopee_order:
                res['location_id'] = int(self.env['ir.config_parameter'].sudo().get_param('shopee_stock'))
        return res
