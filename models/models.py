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


class UploadXMLWizard(models.TransientModel):
    _inherit = "sii.dte.upload_xml.wizard"

    def _prepare_line(self, line, document_id, type, company_id, fpos_id, price_included=False, exenta=False):
        data = {}
        product_id = self._buscar_producto(document_id, line, company_id, price_included, exenta)
        if isinstance(product_id, int):
            data.update(
                {"product_id": product_id,}
            )
        elif not product_id:
            return False
        price_subtotal = float(line.find("MontoItem").text)
        try:
            qtyItem=float(line.find("QtyItem").text)    
        except Exception as ex:
            _logger.error(tools.ustr(ex))
            qtyItem=1

        price = float(line.find("PrcItem").text) if line.find("PrcItem") is not None else price_subtotal
        subTotal=qtyItem*price
        if line.find("DescuentoPct") is not None:
            discount = float(line.find("DescuentoMonto").text)        
            discount = float(line.find("DescuentoPct").text)
        elif line.find("DescuentoMonto") is not None:
            discount = float(line.find("DescuentoMonto").text)        
            discount = (discount/subTotal)*100
        else:
            discount=0
        
        DescItem = line.find("DescItem")
        data.update(
            {
                "sequence": line.find("NroLinDet").text,
                "name": DescItem.text if DescItem is not None else line.find("NmbItem").text,
                "price_unit": price,
                "discount": discount,
                "quantity": line.find("QtyItem").text if line.find("QtyItem") is not None else 1,
                "price_subtotal": price_subtotal,
            }
        )
        if self.pre_process and self.type == "compras":
            data.update(
                {"new_product": product_id, "product_description": DescItem.text if DescItem is not None else "",}
            )
        else:
            product_id = self.env["product.product"].browse(product_id)
            fpos = self.env["account.fiscal.position"].browse(fpos_id)
            account = self.env["account.invoice.line"].get_invoice_line_account(type, product_id, fpos, company_id)
            IndExe = line.find("IndExe")
            amount = 0
            sii_code = 0
            sii_type = False
            tax_ids = self.env["account.tax"]
            if IndExe is None and not exenta:
                amount = 19
                sii_code = 14
                sii_type = False
            else:
                IndExe = True
            tax_ids += self._buscar_impuesto(
                type="purchase" if self.type == "compras" else "sale",
                amount=amount, sii_code=sii_code, sii_type=sii_type,
                IndExe=IndExe, company_id=company_id
            )
            if line.find("CodImpAdic") is not None:
                amount = 19
                sii_type = False
                tax_ids += self._buscar_impuesto(
                    type="purchase" if self.type == "compras" else "sale",
                    amount=amount, sii_code=line.find("CodImpAdic").text,
                    sii_type=sii_type, IndExe=IndExe, company_id=company_id
                )
            if IndExe is None:
                tax_include = False
                for t in tax_ids:
                    if not tax_include:
                        tax_include = t.price_include
                if price_included and not tax_include:
                    base = price
                    price = 0
                    base_subtotal = price_subtotal
                    price_subtotal = 0
                    for t in tax_ids:
                        if t.amount > 0:
                            price += base / (1 + (t.amount / 100.0))
                            price_subtotal += base_subtotal / (1 + (t.amount / 100.0))
                elif not price_included and tax_include:
                    price = tax_ids.compute_all(price, self.env.user.company_id.currency_id, 1)["total_included"]
                    price_subtotal = tax_ids.compute_all(price_subtotal, self.env.user.company_id.currency_id, 1)[
                        "total_included"
                    ]

            data.update(
                {
                    "account_id": account.id,
                    "invoice_line_tax_ids": [(6, 0, tax_ids.ids)],
                    "uom_id": product_id.uom_id.id,
                    "price_unit": price,
                    "price_subtotal": price_subtotal,
                }
            )
        return [0, 0, data]