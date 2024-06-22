from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def woo_update_quantity(self):
        location_id = self.env['stock.location'].browse(int(self.env['ir.config_parameter'].sudo().get_param('woo_stock')))
        if self.product_id.is_manage_stock and self.location_id == location_id:
            # and self.location_id == location_id:
            connector = self.env['corsiva.woo'].open(connector_type='woo')
            data = self._prepare_data_to_update_quantity_woo()
            connector.woo_update_product(data=data, id_woo=self.product_id.id_woo)

    def _prepare_data_to_update_quantity_woo(self):
        if self.quantity == 0:
            stock_status = "outofstock"
        elif self.quantity > 0:
            stock_status = "instock"
        else:
            stock_status = "onbackorder"
        return {
                "stock_quantity": self.quantity,
                "stock_status": stock_status
                }
