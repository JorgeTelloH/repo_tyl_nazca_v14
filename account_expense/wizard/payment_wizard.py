# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
import logging
#_logger = logging.getLogger(__name__)

class PaymentWizard(models.TransientModel):
    _name = 'account.expense.payment'
    _description = 'Pagos de Gastos'

    date = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True)
    document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
    document_nbr = fields.Char(string='Nro Documento', size=20, required=True)
    journal_expense_id = fields.Many2one('account.journal', string='Diario', required=True,
                                         domain=[('type', 'in', ('bank', 'cash'))])
    amount = fields.Float(string='Monto de pago', digits='Product Price')
    expense_id = fields.Many2one('account.expense', 'Gasto')
    amount_pending = fields.Float(string='Monto de pendiente', digits='Product Price')
    payment_difference = fields.Float(string='Monto diferencia', digits='Product Price')
    payment_difference_handling = fields.Selection([('open', 'Mantener abierto'), ('reconcile', 'Marcar como pagado')],
                                                   default='open', string="Diferencia de pago")
    writeoff_account_id = fields.Many2one('account.account', string="Contanbilizar la diferencia en",
                                          domain=[('deprecated', '=', False)], copy=False)

    journal_writeoff_id = fields.Many2one('account.journal', string='Diario de diferencia')


    @api.model
    def default_get(self, fields):
        rec = super(PaymentWizard, self).default_get(fields)
        obj_expense = self.env['account.expense']
        expense = obj_expense.browse([self.env.context['active_id']])
        if expense:
            rec['amount'] = expense.balance
            rec['amount_pending'] = expense.balance
            rec['journal_expense_id'] = expense.journal_expense_id.id
            rec['currency_id'] = expense.currency_id.id
            rec['document_type_id'] = expense.document_type_id.id
            rec['expense_id'] = expense.id

        return rec

    @api.onchange('amount')
    def onchange_amount(self):
        self.payment_difference = self.amount_pending - self.amount
        if self.amount_pending - self.amount == 0:
            self.payment_difference_handling = 'reconcile'


    def action_generate(self):
        payment_obj = self.env['account.payment']
        payment_method_id = self.journal_expense_id.inbound_payment_method_ids[0].id
        if self.amount < 0:
            payment_type = 'outbound'
            partner_type = 'supplier'
            commu = ' rembolso'
            account_id = self.expense_id.payable_account_id.id
        if self.amount > 0:
            payment_type = 'inbound'
            partner_type = 'customer'
            account_id = self.expense_id.account_id.id
            commu = ' cobro'

        payment_vals = {
            'payment_type': payment_type,
            'partner_type': partner_type,
            'partner_id': self.expense_id.partner_id.id,
            'amount': abs(self.amount),
            'journal_id': self.journal_expense_id.id,
            'date': self.date,
            'ref': self.expense_id.name + commu,
            'payment_method_id': payment_method_id,
            'expense_id': self.expense_id.id,
            'destination_account_id': account_id,
            'currency_id': self.expense_id.currency_id.id,
            'l10n_latam_document_type_id': self.document_type_id.id,
            'document_nbr': self.document_nbr,
        }

        pendig = round(self.amount_pending - self.amount,2)
        if pendig and self.payment_difference_handling == 'reconcile':
            payment_vals['write_off_line_vals'] = {
                'name': 'Diferencia de cambio',
                'amount': pendig,
                'account_id': self.writeoff_account_id.id,
            }
            pendig = 0

        payments = payment_obj.with_context(skip_account_move_synchronization=True).create(payment_vals)

        writeoff_acc_id = False
        writeoff_journal_id = False
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_acc_id=self.writeoff_account_id
            writeoff_journal_id=self.journal_writeoff_id

        payments.action_post()
        #new_balance = self.amount_pending - self.payment_difference - self.amount
        self.expense_id.expense_payment(payments,account_id,self.amount_pending,pendig,writeoff_acc_id,writeoff_journal_id)

        return


class RegisterPaymentWizard(models.TransientModel):
    _name = 'account.register.expense.payment'
    _description = 'Registro de Pago de Gastos'

    date = fields.Date(string='Fecha', required=True, default=fields.Date.context_today)
    document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
    document_nbr = fields.Char(string='Nro Documento', size=20, required=True)
    journal_expense_id = fields.Many2one('account.journal', string='Diario', required=True,
                                         domain=[('type', 'in', ('bank', 'cash'))])
    amount = fields.Float(string='Monto de pago', digits='Product Price')

    def action_generate(self):
        payment_obj = self.env['account.payment']
        obj_expense = self.env['account.expense']
        expense = obj_expense.browse([self.env.context['active_id']])
        payment_method_id = self.journal_expense_id.inbound_payment_method_ids[0].id
        payment = payment_obj.with_context(skip_account_move_synchronization=True).create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',
            'partner_id': expense.partner_id.id,
            'amount': self.amount,
            'journal_id': self.journal_expense_id.id,
            'date': self.date,
            'ref': expense.name,
            'payment_method_id': payment_method_id,
            'expense_id': expense.id,
            'destination_account_id': expense.account_id.id,
            'currency_id': expense.currency_id.id,
            'l10n_latam_document_type_id': self.document_type_id.id,
            'document_nbr': self.document_nbr,
        })
        payment.action_post()
        expense.get_expense_amount()

