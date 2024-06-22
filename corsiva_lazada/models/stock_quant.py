from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def update_quantity(self):
        location_id = self.env['stock.location'].browse(
            int(self.env['ir.config_parameter'].sudo().get_param('lazada_stock')))
        if location_id and self.product_id.sku_id and self.location_id == location_id:
            connector = self.env['corsiva.connector'].open(connector_type='lazada')
            data = self._prepare_data_to_update_quantity()
            connector.update_quantity('update_quantity', data=data)

    def _prepare_data_to_update_quantity(self):
        return {
            "Request": {
                "Product": {
                    "Skus": {
                        "Sku": [{
                            "SkuId": self.product_id.sku_id,
                            "ItemId": self.product_id.item_id,
                            "SellableQuantity": self.quantity
                        }]
                    }
                }
            }
        }
