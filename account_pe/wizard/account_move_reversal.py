# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    show_journal = fields.Boolean(string='Reason', default=True)

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res['forma_pago']='Contado'
        return res


    @api.depends('move_ids')
    def _compute_document_type(self):
        res = super()._compute_document_type()
        self.l10n_latam_available_document_type_ids = False
        self.l10n_latam_document_type_id = False
        self.l10n_latam_use_documents = False
        for record in self:
            if len(record.move_ids) > 1:
                move_ids_use_document = record.move_ids._origin.filtered(lambda move: move.l10n_latam_use_documents)
                if move_ids_use_document:
                    raise UserError(_('You can only reverse documents with legal invoicing documents from Latin America one at a time.\nProblematic documents: %s') % ", ".join(move_ids_use_document.mapped('name')))
            else:
                record.l10n_latam_use_documents = record.move_ids.journal_id.l10n_latam_use_documents

            if record.l10n_latam_use_documents:
                refund = record.env['account.move'].new({
                    'move_type': record._reverse_type_map(record.move_ids.move_type),
                    'journal_id': record.move_ids.journal_id.id,
                    'partner_id': record.move_ids.partner_id.id,
                    'company_id': record.move_ids.company_id.id,
                })
                l10n_latam_available_document_type_ids = refund.mapped("l10n_latam_available_document_type_ids").filtered(
                    lambda x: x.code == "07"
                )
                l10n_latam_document_type_id = refund.mapped("l10n_latam_available_document_type_ids").filtered(
                    lambda x: x.code == "07"
                )
                if not l10n_latam_document_type_id:
                    type = self.env['l10n_latam.document.type'].search([('code','=','07')])
                    l10n_latam_document_type_id +=type
                    if not type in l10n_latam_available_document_type_ids:
                        l10n_latam_available_document_type_ids += type

                record.l10n_latam_document_type_id = l10n_latam_document_type_id[0]
                record.l10n_latam_available_document_type_ids = l10n_latam_available_document_type_ids

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get(
            'active_model') == 'account.move' else self.env['account.move']
        move_type = (len(move_ids) > 1 or move_ids.move_type == 'entry') and 'cancel' or move_ids.move_type
        if move_type == 'in_invoice':
            res['show_journal'] = False
        return res

    def reverse_moves(self):
        res = super(AccountMoveReversal, self).reverse_moves()
        res.update({
            'context': {'default_move_type': 'out_refund'}}
        )
        return res
