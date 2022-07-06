# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools import float_compare, float_is_zero

import logging
#_logger = logging.getLogger(__name__)

class Expense(models.Model):
    _name = 'account.expense'
    _description = "Rendicion de Gastos de Personal"

    name = fields.Char(string='Gasto', required=True, readonly=True, index=True, default='Nuevo')
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('approved', 'Aprobado'),
         ('done', 'Realizado'),
         ('rembolso', 'Rembolso'),
         ('cobro', 'Cobro'),
         ('refused', 'Rechazado')],
        readonly=True, default='draft', index=True, string='Estado')
    date = fields.Date(string='Fecha', required=True, readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, readonly=True,
        states={'draft': [('readonly', False)]}, default=lambda self: self.env.user.company_id.currency_id)
    expense_amount = fields.Float(string='Monto de gasto', digits='Product Price', default=0.0,
        readonly=True, states={'draft': [('readonly', False)]})
    invoice_balance = fields.Float(string='Saldo de Comprobantes', readonly=True, store=True)
    balance = fields.Float(compute='_compute_amount', string='Saldo', readonly=True, store=True)
    invoice_ids = fields.One2many('account.move', 'expense_inv_id', string='Comprobantes', copy=False)
    partner_id = fields.Many2one('res.partner', string='Personal', required=True, 
        readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id, readonly=True)
    payment_ids = fields.One2many('account.payment', 'expense_id', string='Pagos', copy=False, auto_join=True)
    account_id = fields.Many2one('account.account', string="Cuenta contable", required=True)
    rendi_move_id = fields.Many2one('account.move', string='Asiento rendicion', readonly=True)
    payable_account_id = fields.Many2one('account.account', string="Cuenta por pagar al colaborador")
    note = fields.Char(string='Nota', required=True, readonly=True, states={'draft': [('readonly', False)]})
    document_type_id = fields.Many2one('l10n_latam.document.type', string='Tipo Documento')
    document_nbr = fields.Char(string='Nro Documento', size=20)
    journal_expense_id = fields.Many2one('account.journal', string='Diario salida de dinero', required=True,
                                         readonly = True,
                                         states = {'draft': [('readonly', False)]},
                                         domain=[('type', 'in', ('bank', 'cash'))])

    mv_count = fields.Integer(string='Conteo Asiento Contable', compute='_mv_count', copy=False)

    def _mv_count(self):
        amv_ids = self.rendi_move_id
        self.mv_count = len(amv_ids)

    def action_view_mv(self):
        self.ensure_one()
        moves = self.rendi_move_id
        act_move = {
            'name': _('Apunte Contable'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', moves.ids or moves.id)],
            'context': self._context,
            'type': 'ir.actions.act_window',
        }
        return act_move


    def get_expense_amount(self):
        amount = 0
        for payment in self.payment_ids:
            if not payment.state in ['cancelled']:
                amount += payment.amount

        self.write({'expense_amount':amount})

        return amount

    @api.onchange('partner_id')
    def _partner(self):
        if self.partner_id:
            self.account_id = self.partner_id.property_account_expense_receivable_id or self.company_id.account_expense_reci
            self.payable_account_id = self.partner_id.property_account_expense_payable_id or self.company_id.account_expense_pay



    @api.onchange('invoice_ids')
    def _compute_amount_invoice(self):
        # Calcular el total de Comprobantes
        for rec in self:
            amount_inv = 0
            for d_inv in rec.invoice_ids:
                if d_inv.state not in ['draft', 'cancel']:
                    if d_inv.currency_id != self.currency_id:
                        ammt_expn = d_inv.currency_id._convert(abs(d_inv.amount_total or d_inv.amount_residual_signed),
                                                               self.currency_id, d_inv.company_id, d_inv.invoice_date)
                        amount_inv += ammt_expn
                    else:
                        ammt_expn = d_inv.currency_id._convert(abs(d_inv.amount_total or d_inv.amount_residual_signed), self.currency_id,
                                                               d_inv.company_id, d_inv.invoice_date)
                        amount_inv += ammt_expn
            rec.invoice_balance = amount_inv
        return

    @api.depends('expense_amount', 'invoice_balance')
    def _compute_amount(self):
        for element in self:
            element.balance = element.expense_amount - element.invoice_balance
        return

    def action_return_payments(self):
        if self.rendi_move_id:
            raise ValidationError(_('Debe eliminar el asiento rendicion'))
        self.state = 'approved'
        return

    def action_approved(self):
        payment_obj = self.env['account.payment']

        for rec in self:
            amount_inv = 0
            for d_inv in rec.invoice_ids:
                if d_inv.state not in ['draft', 'cancel']:
                    amount_inv = d_inv.amount_residual_signed + amount_inv

            if rec.expense_amount <= 0:
                raise ValidationError(_('Debe ingresar un monto de gasto mayor a cero!'))
            if not rec.journal_expense_id:
                raise ValidationError(_('Debe Configurar un diario de gastos'))
            if not rec.journal_expense_id.payment_credit_account_id:
                raise ValidationError(_('Configure las cuentas en el diario de gastos'))

            if rec.company_id:
                name = self.env['ir.sequence'].with_context(force_company=rec.company_id.id).next_by_code('expense') or 'Nuevo'
            else:
                name = self.env['ir.sequence'].next_by_code('expense') or 'Nuevo'

            rec.name = name

            payment_method_id = rec.journal_expense_id.inbound_payment_method_ids[0].id
            payment = payment_obj.with_context(skip_account_move_synchronization=True).create({
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'partner_id': rec.partner_id.id,
                'amount': rec.expense_amount,
                'journal_id':rec.journal_expense_id.id,
                'date':rec.date,
                'ref':rec.name + " " + rec.note,
                'payment_method_id':payment_method_id,
                'expense_id': rec.id,
                'destination_account_id':rec.account_id.id,
                'currency_id':rec.currency_id.id,
                'l10n_latam_document_type_id':rec.document_type_id.id,
                'document_nbr':rec.document_nbr,
            })
            payment.action_post()
            rec.state = 'approved'
            rec.invoice_balance = amount_inv

    def action_refused(self):
        for rec in self:
            #Validar que los Comprobantes No esten pagados
            for d_inv in self.invoice_ids:
                if d_inv.state == 'paid':
                    raise ValidationError(_("Los Comprobantes No deben estar en Estado: 'Pagado'!"))
            #Validar que los Pagos No esten conciliados
            for d_pay in self.payment_ids:
                if d_pay.state == 'reconciled':
                    raise ValidationError(_("Los Pagos No deben estar en Estado: 'Conciliado'!"))
            rec.state = 'refused'

    def action_reconcile_pay(self):
        amount_inv = 0
        if not self.company_id.journal_expense_id:
            raise ValidationError(_("Configure los diarios de gastos en la compañia!"))
        for d_inv in self.invoice_ids:
            if d_inv.state not in ['draft', 'cancel']:
                ammt_expn = d_inv.currency_id._convert(abs(d_inv.amount_total or d_inv.amount_residual_signed),
                                                       self.currency_id, d_inv.company_id, d_inv.invoice_date)
                amount_inv += ammt_expn

        move_lines = self.create_lines_move()
        move = self.env['account.move'].create({
            'ref': 'GASTO RENDIDO ' + self.name,
            'date': fields.Date.today(),
            #'process_account_date': fields.Date.today(),
            #'period_id': v_period_id,
            'journal_id': self.company_id.journal_expense_id.id,
            'currency_id':self.currency_id.id,
        })
        move.write({'line_ids': move_lines})  # agregamos al move
        move.post()  # Validamos
        self.rendi_move_id = move
        reconciles_pay = False
        for payment in self.payment_ids:
            for line_payment in payment.move_id.line_ids:
                for line_move in move.line_ids:
                    name1= payment.name
                    name2= line_move.name
                    account1 = line_payment.account_id
                    account2 = line_move.account_id
                    part1 = line_payment.partner_id
                    part2 = line_move.partner_id
                    if line_payment.account_id == line_move.account_id and line_payment.partner_id == line_move.partner_id:
                        if line_payment.amount_residual != 0 and line_move.amount_residual != 0:
                            (line_payment+line_move).reconcile()
        # if reconciles_pay:
        #     reconciles_pay.reconcile()
        for invoice in self.invoice_ids:
            for line_invoice in invoice.line_ids:
                for line_move in move.line_ids:
                    name1 = invoice.ref
                    if name1 == line_move.name and line_invoice.account_id == line_move.account_id and line_invoice.partner_id == line_move.partner_id:
                        if line_invoice.amount_residual != 0 and line_move.amount_residual != 0:
                            (line_invoice + line_move).reconcile()

        self.invoice_balance = amount_inv
        precision = self.env['decimal.precision'].precision_get('Account')
        balan = self.expense_amount - amount_inv
        if (self.expense_amount - amount_inv) < 0:
            self.state = 'rembolso'
        if (self.expense_amount - amount_inv) > 0:
            self.state = 'cobro'
        if (self.expense_amount - amount_inv) == -0:
            self.state = 'done'
        if float_is_zero(balan, precision):
            self.state = 'done'
            self.write({'state':'done'})

        return

    def action_return_reconcile(self):
        if self.rendi_move_id:
            for line in self.rendi_move_id.line_ids:
                line.remove_move_reconcile()
            self.rendi_move_id.button_cancel()
            self.rendi_move_id.with_context(force_delete=True).unlink()
            #self.rendi_move_id.unlink()
            self.state = 'approved'

        return

    def action_calculate_balances(self):
        self.get_expense_amount()
        for rec in self:
            amount_inv = 0
            for d_inv in rec.invoice_ids:
                if d_inv.state not in ['draft', 'cancel']:
                    if d_inv.currency_id != self.currency_id:
                        ammt_expn = d_inv.currency_id._convert(abs(d_inv.amount_total or d_inv.amount_residual_signed),
                                                               self.currency_id, d_inv.company_id, d_inv.invoice_date)
                        amount_inv += ammt_expn
                        #amount_inv = abs(d_inv.amount_residual_signed) + amount_inv
                    else:
                        ammt_expn = d_inv.currency_id._convert(abs(d_inv.amount_total or d_inv.amount_residual_signed), self.currency_id,
                                                               d_inv.company_id, d_inv.invoice_date)
                        amount_inv += ammt_expn
                        #amount_inv = abs(d_inv.amount_residual_signed) + amount_inv
                rec.invoice_balance = amount_inv
        return

    def action_payment(self):
        payment_obj = self.env['account.payment']
        for rec in self:
            payment_method_id = rec.journal_expense_id.inbound_payment_method_ids[0].id
            if rec.balance < 0:
                payment_type = 'outbound'
                partner_type = 'supplier'
                commu = ' rembolso'
                account_id = self.payable_account_id.id or self.partner_id.property_account_payable_id.id
            if rec.balance > 0:
                payment_type = 'inbound'
                partner_type = 'customer'
                account_id = self.account_id.id
                commu = ' cobro'

            payments = payment_obj.with_context(skip_account_move_synchronization=True).create({
                'payment_type': payment_type,
                'partner_type': partner_type,
                'partner_id': rec.partner_id.id,
                'amount': abs(rec.balance),
                'journal_id': rec.journal_expense_id.id,
                'payment_date': rec.date,
                'communication': rec.name + commu,
                'payment_method_id': payment_method_id,
                'expense_id': rec.id,
                'force_destination_account_id': account_id,
                'currency_id': rec.currency_id.id,
                'document_type_id': rec.document_type_id.id,
                'document_nbr': rec.document_nbr,
            })
            payments.post()
            lines_to_roconcile = False
            for payment in payments:
                for line_payment in payment.move_id.line_ids:
                    cuenta = line_payment.account_id.code
                    if line_payment.account_id.id == account_id:
                        if lines_to_roconcile:
                            lines_to_roconcile+line_payment
                        else:
                            lines_to_roconcile = line_payment
            if rec.balance < 0:
                for line in rec.rendi_move_id.line_ids:
                    if line.account_id.id == account_id and line.partner_id == rec.partner_id:
                        if lines_to_roconcile:
                            (lines_to_roconcile + line).reconcile()
            if rec.balance > 0:
                for payment in rec.payment_ids:
                    if payment == payments:
                        continue
                    for line_payment in payment.move_id.line_ids:
                        if line_payment.account_id.id == account_id:
                            (lines_to_roconcile + line_payment).reconcile()

            rec.balance = 0
            rec.state = 'done'
        return

    def expense_payment(self, payments, account_id, balance, new_balance,writeoff_acc_id= False, writeoff_journal_id= False):
        for rec in self:
            lines_to_roconcile = False
            for payment in payments:
                for line_payment in payment.move_id.line_ids:
                    if line_payment.account_id.id == account_id:
                        if line_payment.amount_residual != 0:
                            if lines_to_roconcile:
                                lines_to_roconcile + line_payment
                            else:
                                lines_to_roconcile = line_payment
            if balance < 0:
                lines_rendi = False
                for line in rec.rendi_move_id.line_ids:
                    if line.account_id.id == account_id and line.partner_id == rec.partner_id:
                        if line.amount_residual != 0:
                            if lines_rendi:
                                lines_rendi = lines_rendi + line
                            else:
                                lines_rendi = line
                        # if lines_to_roconcile:
                        #     (lines_to_roconcile + line).reconcile()
                if lines_rendi and lines_to_roconcile:
                    es_con = (lines_to_roconcile + lines_rendi).reconcile()
                    #res_con = (lines_to_roconcile+lines_rendi).reconcile(writeoff_acc_id,writeoff_journal_id)
            if balance > 0:
                lines_rendi = False
                for payment in rec.payment_ids:
                    if payment == payments:
                        continue
                    for line_payment in payment.move_id.line_ids:
                        if line_payment.account_id.id == account_id:
                            if line_payment.amount_residual != 0:
                                if lines_rendi:
                                    lines_rendi = lines_rendi + line_payment
                                else:
                                    lines_rendi = line_payment
                                #(lines_to_roconcile + line_payment).reconcile()
                                #(lines_to_roconcile + line_payment).reconcile(writeoff_acc_id, writeoff_journal_id)
                if lines_rendi and lines_to_roconcile:
                    es_con = (lines_to_roconcile + lines_rendi).reconcile()

            rec.balance = new_balance
            if new_balance == 0:
                rec.state = 'done'
        return


    def create_lines_move(self):
        move_lines= []
        total_amount = 0
        total_paymen= 0
        amount_currency_total = 0
        amount_residual_invoices = 0
        amount_total_expense_currency_payments = 0
        amount_total_company_currency_payment = 0
        for payment in self.payment_ids:
            if not payment.state in ['cancelled']:
                if payment.currency_id != self.company_id.currency_id:
                    #amount_total_currency_payments += payment.amount
                    amount_pay = payment.currency_id._convert(abs(payment.amount),
                                               self.company_id.currency_id, self.company_id, payment.date)
                    amount_total_company_currency_payment +=amount_pay
                else:
                    amount_total_company_currency_payment +=payment.amount

                if payment.currency_id != self.currency_id:
                    amount_pay_expense = payment.currency_id._convert(abs(payment.amount),
                                                              payment.currency_id, self.company_id,
                                                              payment.date)

                    amount_total_expense_currency_payments += amount_pay_expense
                else:
                    amount_total_expense_currency_payments += payment.amount

                total_paymen += payment.amount
        move_line_vals = {
            'name': self.name,
            'debit': 0,
            'credit': amount_total_company_currency_payment,
            'amount_currency': -amount_total_expense_currency_payments,
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'date': fields.Date.today(),
            'account_id': self.account_id.id,
        }
        move_lines.append((0, 0, move_line_vals))

        for invoice in self.invoice_ids:

            amount_currency = False
            amount_residual = abs(invoice.amount_residual_signed)
            amount_residual_invoices += amount_residual
            if invoice.currency_id != self.company_id.currency_id:
                amount_currency = invoice.amount_total
                amount_currency_total += invoice.amount_total

            if invoice.currency_id != self.currency_id:
                ammt_expn = invoice.currency_id._convert(abs(invoice.amount_total),
                                                         self.currency_id, invoice.company_id, invoice.invoice_date)
                total_amount += ammt_expn

            else:
                total_amount += invoice.amount_total

            # Creamos linea de factura
            move_line_vals = {
                'name': invoice.ref,
                'debit': amount_residual,
                'credit': 0,
                'amount_currency': amount_currency,
                'partner_id': invoice.partner_id.id,
                'currency_id': invoice.currency_id.id,
                'date': fields.Date.today(),
                'account_id': invoice.account_id.id,
            }
            move_lines.append((0, 0, move_line_vals))

        if (amount_total_expense_currency_payments-total_amount)< 0:
            if not self.payable_account_id:
                raise ValidationError(_("No ha asignado la cuenta por pagar"))

            ammt_expn = self.currency_id._convert(abs(total_paymen-total_amount),
                                                     self.currency_id, self.company_id, fields.Date.today())
            move_line_vals = {
                'name': self.name,
                'debit': 0,
                'credit': round(abs(amount_total_company_currency_payment - amount_residual_invoices),2),
                'amount_currency':round(amount_total_expense_currency_payments - total_amount,2),
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'date': fields.Date.today(),
                'account_id': self.payable_account_id.id or self.partner_id.property_account_payable_id.id,
            }
            move_lines.append((0, 0, move_line_vals))
        if (amount_total_expense_currency_payments-total_amount) > 0:
            if self.currency_id != self.company_id.currency_id:
                move_lines[0][2]['credit'] = move_lines[0][2]['credit'] - (
                            amount_total_company_currency_payment - amount_residual_invoices)
                move_lines[0][2]['amount_currency'] = move_lines[0][2]['amount_currency'] + (
                            amount_total_expense_currency_payments - total_amount)

            else:
                move_lines[0][2]['credit'] = move_lines[0][2]['credit']-(amount_total_company_currency_payment-amount_residual_invoices)


        return move_lines
