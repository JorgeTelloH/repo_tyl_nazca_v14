# -*- coding: utf-8 -*-

import base64
import zipfile
import io
from requests.exceptions import ConnectionError, HTTPError, InvalidSchema, InvalidURL, ReadTimeout
from odoo.exceptions import UserError, ValidationError
from zeep.wsse.username import UsernameToken
from zeep import Client, Settings
from zeep.exceptions import Fault
from zeep.transports import Transport
from lxml import etree
from lxml.objectify import fromstring
from copy import deepcopy

from odoo import models, fields, api, _, _lt
from ..tools.nubefact import nubefact_jsonrpc
from ..tools.nubefact import nubefact_convert_data
from odoo.tools.pdf import OdooPdfFileReader, OdooPdfFileWriter


from odoo.exceptions import AccessError
from odoo.tools import html_escape


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'


    def _l10n_pe_edi_sign_invoices_nubefact(self, invoice, edi_filename, edi_str):
        #_l10n_pe_edi_sign_invoices_iap
        credentials = self._l10n_pe_edi_get_sunat_nubefact(invoice.company_id)
        url = self.get_url_nubefact(invoice)
        edi_values = self._l10n_pe_edi_get_edi_values(invoice)
        data_values = nubefact_convert_data(invoice,edi_values)
        result = nubefact_jsonrpc(url, params=data_values, credentials=credentials, timeout=1500)

        #result = iap_jsonrpc(url, params=rpc_params, timeout=1500)
        #message = "Factura creada en facturaonline.pe " + "id de Factura " + result.get("idFactura")
        return result

    def _l10n_pe_edi_get_sunat_nubefact(self, company):
        self.ensure_one()
        res = {}
        if not company.l10n_pe_edi_endpoint or not company.l10n_pe_edi_token:
            raise UserError(_("Configurar el Endpoint y Token"))
        res.update({
            'enpoint': company.l10n_pe_edi_endpoint,
            'token': company.l10n_pe_edi_token,
        })
        return res

    def get_url_nubefact(self, invoice):
        url = invoice.company_id.l10n_pe_edi_endpoint_facturaonline
        return url


