# -*- coding: utf-8 -*-
# from odoo import http


# class NominasSudamerisHcs(http.Controller):
#     @http.route('/hcs_argonconsultora/hcs_argonconsultora/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hcs_argonconsultora/hcs_argonconsultora/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hcs_argonconsultora.listing', {
#             'root': '/hcs_argonconsultora/hcs_argonconsultora',
#             'objects': http.request.env['hcs_argonconsultora.hcs_argonconsultora'].search([]),
#         })

#     @http.route('/hcs_argonconsultora/hcs_argonconsultora/objects/<model("hcs_argonconsultora.hcs_argonconsultora"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hcs_argonconsultora.object', {
#             'object': obj
#         })
