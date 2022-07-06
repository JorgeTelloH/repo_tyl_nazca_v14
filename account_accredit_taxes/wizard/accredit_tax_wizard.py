# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccreditTaxes(models.TransientModel):
    _name = 'account.accredit.tax'

    date = fields.Date(string='Fecha para acreditar', required=True)
    account_id = fields.Many2one("account.account", string="Cuenta Contable", required=True)
    journal_id = fields.Many2one("account.journal", string="Diario", required=True)
    amount = fields.Float(string='Monto')

    @api.model
    def default_get(self, fields):
        result = super(AccreditTaxes, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        if res_ids:
            move_org = self.env['account.move'].browse(res_ids)
            amount_tax = 0
            amount_tax_currency = 0
            for tax in move_org.l10n_latam_tax_ids:
                amount_tax += tax.balance
                amount_tax_currency += tax.amount_currency
            result['amount'] = amount_tax_currency or amount_tax
        return result

    def action_generate(self):
        res_ids = self._context.get('active_ids')
        moves = []
        if res_ids:
            move_org = self.env['account.move'].browse(res_ids)
            amount_tax = 0
            amount_tax_currency = 0

            for tax in move_org.l10n_latam_tax_ids:
                amount_tax += tax.balance
                amount_tax_currency += tax.amount_currency
                move_line_vals1 = {
                    'name': move_org.ref,
                    'debit': tax.credit,
                    'credit': tax.debit,
                    'amount_currency': abs(tax.amount_currency) if tax.credit >0 else tax.amount_currency*-1,
                    'partner_id': move_org.partner_id.id,
                    'currency_id': move_org.currency_id.id,
                    'date': self.date,
                    'account_id': move_org.account_id.id,
                }

                moves.append((0, 0, move_line_vals1))
                move_line_vals2 = {
                    'name': move_org.ref,
                    'debit': tax.debit,
                    'credit': tax.credit,
                    'amount_currency': tax.amount_currency,
                    'partner_id': move_org.partner_id.id,
                    'currency_id': move_org.currency_id.id,
                    'date': self.date,
                    'account_id': self.account_id.id,
                }
                moves.append((0, 0, move_line_vals2))

            if moves:
                move = self.env['account.move'].create({
                    'ref': '%s %s '  % (move_org.partner_id.name, move_org.ref),
                    'date': self.date,
                    'invoice_date':self.date,
                    'journal_id': self.journal_id.id,
                    'currency_id': move_org.currency_id.id,
                    'is_accredit_move':True,
                })
                move.write({'line_ids': moves})
                move_org.write({'accredit_move_id':move.id})
        return