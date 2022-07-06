# -*- coding: utf-8 -*-
from odoo import api,fields,models,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter
import time
import hmac
import hashlib
import requests
import base64
import io
import logging
import pathlib
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    pdf_url = fields.Char(string='Descargar PDF', readonly=True, copy=False)

    @api.depends('amount_by_group')
    def _get_percentage_igv(self):
        for move in self:
            igv = 0.0
            tax_igv_group_id = self.env['account.tax.group'].search([('name' ,'=' ,'IGV')], limit=1)
            if tax_igv_group_id:
                tax_id = self.env['account.tax'].search([('tax_group_id' ,'=' ,tax_igv_group_id.id)], limit=1)
                if tax_id:
                    igv = int(tax_id.amount)
                    return igv
        return False

    def generate_invoice_print(self):
        values = super().generate_invoice_print()
        if not self.pdf_invoice:
            edi_document_ids = self.edi_document_ids
            for doc in edi_document_ids:
                if doc.pdf_url:
                    if len(doc.pdf_url) >1:
                        name, pdf = self.get_nubefect_pdf_by_url(doc.pdf_url)
                        if pdf:
                            self.write({'pdf_name_invoice': name,
                                        'pdf_invoice': pdf})
                            datas = base64.b64decode(pdf)
                            return {'name': name, 'datas': datas}

        return values

    def get_nubefect_pdf_by_url(self, url):

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if response.status_code == 200:
                pdf = response.content
                base = base64.b64encode(pdf)
                name = self.name.replace(' ', '') + '.pdf'
                return name, base
        except requests.exceptions.HTTPError as httpe:
            _logger.warning('HTTP error %s with the given URL: %s' % (httpe.code, url))
            return
        return