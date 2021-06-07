import base64
import logging

from facturacion_electronica import facturacion_electronica as fe
from lxml import etree
from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)



class ModuleName(models.Model):
    _inherit = 'mail.message.dte.document.line'

    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'),default=0.0)# -*- coding: utf-8 -*-

