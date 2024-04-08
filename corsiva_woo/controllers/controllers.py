# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

import requests
import json
import time


class WooControllers(http.Controller):
    @http.route('/woo-lazada', type='http', auth='public', csrf=False, methods=['POST'])
    def woo_webhook_handler(self, **post):
        try:
            data = json.loads(request.httprequest.data)
            request.env["sale.order"].sudo().add_order_to_odoo(data=data)
        except Exception as e:
            raise ValidationError(str(e))
        return http.Response('OK', status=200)