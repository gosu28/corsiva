from . import models

from odoo import api, SUPERUSER_ID


def _stock_post_init(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_record = env.ref('stock.stock_location_stock')
    if xml_record:
        env.ref('corsiva_setup.lazada_stock_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.shopee_stock_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.woo_stock_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.ecommerce_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.shopee_n_lazada_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.shopee_n_woo_location').location_id = xml_record.location_id.id
        env.ref('corsiva_setup.woo_n_lazada_location').location_id = xml_record.location_id.id
