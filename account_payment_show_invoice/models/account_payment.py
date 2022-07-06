# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    invoice_number = fields.Char(string='Documentos', compute='_compute_invoice_number', store=True, copy=False)


    @api.depends('reconciled_invoice_ids', 'reconciled_bill_ids')
    def _compute_invoice_number(self):
        for rec in self:
            doc_nbr = ''
            #Documento de Cliente
            for c_invoice in rec.reconciled_invoice_ids:
                if doc_nbr:
                    doc_nbr += ', '
                doc_nbr += c_invoice.name
            #Documento de Proveedor
            for v_invoice in rec.reconciled_bill_ids:
                if doc_nbr:
                    doc_nbr += ', '
                doc_nbr += v_invoice.ref

            rec.invoice_number = doc_nbr
