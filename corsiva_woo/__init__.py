
from . import controllers
from . import models

from odoo import api, SUPERUSER_ID


def _stock_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_record = env.ref('stock.stock_location_stock')
    if xml_record:
        env.ref('corsiva_woo.woo_stock_location').location_id = xml_record.location_id.id