from odoo import api, fields, models
from odoo.tools.misc import formatLang


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_woo_order = fields.Boolean()
    woo_order_id = fields.Char('Woo order', readonly=False)
    woo_status = fields.Char('Woo status', readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def add_order_to_odoo(self, data=None):
        if data is None:
            raise ValueError("Data Null !")
        order = self.prepare_create_sale_order(data)
        order_id = self.env["sale.order"].create(order)
        order_id.order_line.tax_id = None
        order_id.action_confirm()
        return order_id

    def prepare_create_sale_order(self, data):
        get_order = {
            "partner_id": self.get_customer(partner_id=data["customer_id"], data=data['billing']),
            "woo_order_id": data["id"],
            "woo_status": data["status"],
            "shipping_fee": data["shipping_total"],
            "discount": data["discount_total"],
            "order_line": self.get_sale_order_lines(data=data["line_items"]),
            "type_ecommerce": self.add_type_ecommerce("WooEcommerce")

        }
        return get_order

    def get_sale_order_lines(self, data):
        order_lines = []
        for product in data:
            product_template_id = self.env['product.template'].sudo().search([('id_woo', '=', product['product_id'])])
            line = (0, 0, {'product_id': product_template_id.product_variant_id.id,
                                 'product_uom_qty': product["quantity"]})
            order_lines.append(line)
        return order_lines

    def get_customer(self, partner_id, data):
        data = {
            "name": data["last_name"] + " " + data["first_name"],
            "phone": data["phone"],
            "email": data["email"],
            "street": data["address_1"],
            "street2": data["address_2"],
            "city": data["city"],
            "zip": data["postcode"]
            # "zip": data["postcode"],
            # "country": "SG",
        }
        partner = self.env['res.partner'].search_customers_woo(partner_id, data)
        return partner
