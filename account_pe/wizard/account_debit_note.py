# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    l10n_latam_document_type_id = fields.Many2one('l10n_latam.document.type', 'Tipo de documento', ondelete='cascade',
                                                  domain="[('id', 'in', l10n_latam_available_document_type_ids)]",
                                                  compute='_compute_document_type', readonly=False)
    l10n_latam_available_document_type_ids = fields.Many2many('l10n_latam.document.type',
                                                              compute='_compute_document_type')

    @api.depends('move_ids')
    def _compute_document_type(self):
        self.l10n_latam_available_document_type_ids = False
        self.l10n_latam_document_type_id = False
        move = False
        if self._context.get('active_id'):
            move = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        for record in self:
            domain = [('code','=','08')]
            if move:
                if move.move_type == 'in_invoice':
                    domain.append(('type','=','purchase'))
                if move.move_type == 'out_invoice':
                    domain.append(('type', '=', 'sale'))
            type = self.env['l10n_latam.document.type'].search(domain)
            if type:
                record.l10n_latam_document_type_id = type[0]
                record.l10n_latam_available_document_type_ids = type

    def _prepare_default_values(self, move):
        res = super()._prepare_default_values(move)
        res['is_note_debit'] = True
        res['forma_pago'] = 'Contado'
        type = self.l10n_latam_document_type_id
        if type:
            res['l10n_latam_document_type_id'] = type.id
            type_Default = self.env['account.journal'].browse(res.get('journal_id')).mapped("l10n_latam_document_type_id").filtered(
                lambda x: x.code == "07"
            )
            # if not type in type_Default:
            #     journal_id = self.env['account.journal'].search([('l10n_latam_document_type_id', 'in', [type.id])], limit=1)
            #     if journal_id:
            #         res['journal_id'] = journal_id.id


        return res


    def create_debit(self):
        res = super().create_debit()
        res['context'] = {'default_move_type':'out_invoice'}
        return res





