from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_woo_partner = fields.Boolean(String="is Woo Partner")
    woo_partner_id = fields.Char(String='Partner ID Woo')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        return res

    def search_customers_woo(self, partner_id, data):
        partner = self.env['res.partner'].search([('woo_partner_id', '=', partner_id)])
        if partner:
            return partner.id
        if data['name'] == "":
            if data['email'] == "":
                data['name'] = "Customer {0} Woo".format(partner_id)
            else:
                data['name'] = data['email']
        data['woo_partner_id'] = partner_id
        partner_new = self.env['res.partner'].create(data)
        return partner_new.id

