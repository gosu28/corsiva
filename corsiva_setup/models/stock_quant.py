from odoo import api, fields, models, _


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        products_tracked_without_lot = []
        for quant in self:
            rounding = quant.product_uom_id.rounding
            if fields.Float.is_zero(quant.inventory_diff_quantity, precision_rounding=rounding) \
                    and fields.Float.is_zero(quant.inventory_quantity, precision_rounding=rounding) \
                    and fields.Float.is_zero(quant.quantity, precision_rounding=rounding):
                continue
            if quant.product_id.tracking in ['lot', 'serial'] and \
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
        self.update_ecommerce_stock()

    def update_ecommerce_stock(self):
        # update quantity in lazada store
        if self.env['ir.module.module'].sudo().search([('name', '=', 'corsiva_lazada'), ('state', '=', 'installed')]):
            try:
                self.update_quantity()
            except Exception as e:
                print(e)

        # update quantity in woo store
        if self.env['ir.module.module'].sudo().search([('name', '=', 'corsiva_woo'), ('state', '=', 'installed')]):
            try:
                self.woo_update_quantity()
            except Exception as e:
                print(e)

        # update quantity in shopee store
        if self.env['ir.module.module'].sudo().search([('name', '=', 'corsiva_shopee'), ('state', '=', 'installed')]):
            try:
                self.update_shopee_quantity()
            except Exception as e:
                print(e)
