# -*- coding: utf-8 -*-
# from odoo import http


# class NominasSudamerisHcs(http.Controller):
#     @http.route('/hcs_sudameris/hcs_sudameris/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hcs_sudameris.listing', {
#             'root': '/hcs_sudameris/hcs_sudameris',
#             'objects': http.request.env['hcs_sudameris.hcs_sudameris'].search([]),
#         })

#     @http.route('/hcs_sudameris/hcs_sudameris/objects/<model("hcs_sudameris.hcs_sudameris"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hcs_sudameris.object', {
#             'object': obj
#         })
