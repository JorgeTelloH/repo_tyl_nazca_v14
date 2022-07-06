# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_create_invoice_type = fields.Boolean("Activar creación por Tipo de Documento", related='company_id.enable_create_invoice_type', readonly=False)
    enable_create_invoice_01 = fields.Boolean("Crear Factura",  related='company_id.enable_create_invoice_01')
    enable_create_invoice_03 = fields.Boolean("Crear Boleta", related='company_id.enable_create_invoice_03')
    type_document_partner_01 = fields.Many2many('l10n_latam.identification.type', related='company_id.type_document_partner_01', 
    	string='Tipo Doc Cliente - Facturas', readonly=False)
    type_document_partner_03 = fields.Many2many('l10n_latam.identification.type', related='company_id.type_document_partner_03',
		string='Tipo Doc Cliente - Boletas', readonly=False)
    type_document_journal_01 = fields.Many2one('account.journal', related='company_id.type_document_journal_01',
		string='Diario Facturas', readonly=False)
    type_document_journal_03 = fields.Many2one('account.journal', related='company_id.type_document_journal_03',
		string='Diario Boletas', readonly=False)
    type_document_01 = fields.Many2one('l10n_latam.document.type', related='company_id.type_document_01',
		string='Tipo Doc Facturas', domain=[('type', '=', 'sale')], readonly=False)
    type_document_03 = fields.Many2one('l10n_latam.document.type', related='company_id.type_document_03',
		string='Tipo Doc Boletas', domain=[('type', '=', 'sale')], readonly=False)
