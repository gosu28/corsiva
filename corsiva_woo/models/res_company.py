# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    woo_consumer_key = fields.Char("Woo Consumer Key")
    woo_consumer_secret = fields.Char("Woo Consumer Secret")
    woo_url = fields.Char("Woo URL BASE")