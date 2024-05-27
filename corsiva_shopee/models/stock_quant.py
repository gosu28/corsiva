from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def update_shopee_quantity(self):
        location_id = self.env['stock.location'].browse(int(self.env['ir.config_parameter'].sudo().get_param('shopee_stock')))
        if location_id and self.location_id == location_id:
            connector = self.env['shopee.connector']
            connector.update_stock(self._prepare_data_to_update_stock())

    def _prepare_data_to_update_stock(self):
        return {
            "item_id": int(self.product_id.shopee_item_id),
            "stock_list": [{"model_id": 0, "seller_stock": [{"stock": int(self.quantity)}]}]
        }
