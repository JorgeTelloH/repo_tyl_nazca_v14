# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_payment(models.Model):
    _inherit = 'account.payment'


    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
    document_nbr = fields.Char(string='Nro Documento', size=20)


class account_payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
    document_nbr = fields.Char(string='Nro Documento', size=20)


    def _create_payment_vals_from_wizard(self):
        res = super(account_payment_register, self)._create_payment_vals_from_wizard()
        res['l10n_latam_document_type_id']= self.l10n_latam_document_type_id.id
        res['document_nbr'] = self.document_nbr
        return res