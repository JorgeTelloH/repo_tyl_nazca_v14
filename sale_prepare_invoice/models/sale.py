# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.company_id.enable_create_invoice_type:
            journal, type_doc = self._get_journal_by_document()
            if journal:
                res['journal_id'] = journal.id
                if type_doc:
                    res['l10n_latam_document_type_id'] = type_doc.id
        return res

    def _get_journal_by_document(self):
        if self.partner_id.l10n_latam_identification_type_id in self.company_id.type_document_partner_01:
            journal = self.company_id.type_document_journal_01
            type_doc = self.company_id.type_document_01
            return journal,type_doc
        if self.partner_id.l10n_latam_identification_type_id in self.company_id.type_document_partner_03:
            journal = self.company_id.type_document_journal_03
            type_doc = self.company_id.type_document_03
            return journal,type_doc
        return False, False
