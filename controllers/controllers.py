# -*- coding: utf-8 -*-
from odoo import http

# class MethodUploadXml(http.Controller):
#     @http.route('/method_upload_xml/method_upload_xml/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/method_upload_xml/method_upload_xml/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('method_upload_xml.listing', {
#             'root': '/method_upload_xml/method_upload_xml',
#             'objects': http.request.env['method_upload_xml.method_upload_xml'].search([]),
#         })

#     @http.route('/method_upload_xml/method_upload_xml/objects/<model("method_upload_xml.method_upload_xml"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('method_upload_xml.object', {
#             'object': obj
#         })