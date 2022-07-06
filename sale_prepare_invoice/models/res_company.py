# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    enable_create_invoice_type = fields.Boolean("Activar creación por Tipo de Documento", default=False)
    enable_create_invoice_01 = fields.Boolean("Crear Factura", default=False)
    enable_create_invoice_03 = fields.Boolean("Crear Boleta", default=False)
    type_document_partner_01 = fields.Many2many('l10n_latam.identification.type', 'document_company_relt_01', string='Tipo Doc Cliente - Facturas')
    type_document_partner_03 = fields.Many2many('l10n_latam.identification.type', 'document_company_relt_02', string='Tipo Doc Cliente - Boletas')
    type_document_journal_01 = fields.Many2one('account.journal',string='Diario Facturas')
    type_document_journal_03 = fields.Many2one('account.journal', string='Diario Boletas')
    type_document_01 = fields.Many2one('l10n_latam.document.type', string='Tipo Doc Facturas')
    type_document_03 = fields.Many2one('l10n_latam.document.type', string='Tipo Doc Boletas')

