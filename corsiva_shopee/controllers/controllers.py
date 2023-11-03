# -*- coding: utf-8 -*-
# from odoo import http


# class CorsivaShopee(http.Controller):
#     @http.route('/corsiva_shopee/corsiva_shopee', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/corsiva_shopee/corsiva_shopee/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('corsiva_shopee.listing', {
#             'root': '/corsiva_shopee/corsiva_shopee',
#             'objects': http.request.env['corsiva_shopee.corsiva_shopee'].search([]),
#         })

#     @http.route('/corsiva_shopee/corsiva_shopee/objects/<model("corsiva_shopee.corsiva_shopee"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('corsiva_shopee.object', {
#             'object': obj
#         })
