from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def update_quantity(self):
        location_id = self.env['stock.location'].browse(int(self.env['ir.config_parameter'].sudo().get_param('lazada_stock')))
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

    def action_apply_inventory(self):
        products_tracked_without_lot = []
        for quant in self:
            rounding = quant.product_uom_id.rounding
            if fields.Float.is_zero(quant.inventory_diff_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.inventory_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.quantity, precision_rounding=rounding):
                continue
            if quant.product_id.tracking in ['lot', 'serial'] and\
                    not quant.lot_id and quant.inventory_quantity != quant.quantity and not quant.quantity:
                products_tracked_without_lot.append(quant.product_id.id)
        # for some reason if multi-record, env.context doesn't pass to wizards...
        ctx = dict(self.env.context or {})
        ctx['default_quant_ids'] = self.ids
        quants_outdated = self.filtered(lambda quant: quant.is_outdated)
        if quants_outdated:
            ctx['default_quant_to_fix_ids'] = quants_outdated.ids
            return {
                'name': _('Conflict in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.inventory.conflict',
                'target': 'new',
                'context': ctx,
            }
        if products_tracked_without_lot:
            ctx['default_product_ids'] = products_tracked_without_lot
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'context': ctx,
            }
        self._apply_inventory()
        self.inventory_quantity_set = False
        # update quantity in lazada store
        self.update_quantity()
