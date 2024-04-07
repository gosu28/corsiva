from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def woo_update_quantity(self):
        location_id = self.env.ref('corsiva_woo.woo_stock_location')
        if self.product_id.is_manage_stock and self.location_id == location_id:
            # and self.location_id == location_id:
            connector = self.env['corsiva.woo'].open(connector_type='woo')
            data = self._prepare_data_to_update_quantity()
            connector.woo_update_product(data=data, id_woo=self.product_id.id_woo)

    def _prepare_data_to_update_quantity(self):
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
        self.woo_update_quantity()
