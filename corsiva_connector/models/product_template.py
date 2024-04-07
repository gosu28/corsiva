from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description = fields.Text(
        string='Description'
    )
    short_description = fields.Text(
        string='Short Description'
    )

    type_ecommerce = fields.Many2many("corsiva.ecommerce", string='Ecommerce')

    def add_type_ecommerce(self, name=None):
        type_ecommerce = self.env["corsiva.ecommerce"].search([("name", "=", name)])
        if type_ecommerce:
            for item in type_ecommerce:
                self.type_ecommerce = (4, item.id)
        else:
            type_ecommerce = self.env["corsiva.ecommerce"].create({
                "name": name,
                "description": name,
            })
            self.type_ecommerce = (4, type_ecommerce.id)


