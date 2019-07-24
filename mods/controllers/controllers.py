# -*- coding: utf-8 -*-
from odoo import http

# class Mods(http.Controller):
#     @http.route('/mods/mods/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mods/mods/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mods.listing', {
#             'root': '/mods/mods',
#             'objects': http.request.env['mods.mods'].search([]),
#         })

#     @http.route('/mods/mods/objects/<model("mods.mods"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mods.object', {
#             'object': obj
#         })