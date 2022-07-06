# -*- coding:utf-8 -*-

from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    commission_type = fields.Selection([('p', 'Percent'), ('a', 'Amount')], default='p', string='Commission Type')
    commission_p = fields.Float(string='Percent')
    commission_value_p = fields.Float(string='Percent Amount')
    commission_value_a = fields.Float(string='Amount')
    commission_value = fields.Float(string='Amount commission')

    @api.onchange('commission_type', 'commission_p', 'commission_value_a', 'amount_total')
    def _onchange_commission(self):
        if self.commission_type == 'p':
            self.commission_value_a = 0
            if self.commission_p > 100 or self.commission_p < 0:
                self.commission_p = 0
                raise ValidationError(_('Enter value between 0-100.'))
            elif self.commission_p != 0:
                self.commission_value_p = self.amount_total * self.commission_p / 100
                self.commission_value = self.commission_value_p
        else:
            self.commission_p = 0
            self.commission_value_p = 0
            if self.commission_value_a > self.amount_total:
                self.commission_value_a = 0
                raise ValidationError(_("Commission value can't be greater than Total."))
            else:
                self.commission_value = self.commission_value_a

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.commission_p > 0 or self.commission_value_a > 0:
            participation = self.env['hr.employee.participation']
            values = {'account_move_id': self.id, 'report_date': self.invoice_date or fields.Date.today()}
            participation.create(values)

        return res


class HrEmployeeParticipation(models.Model):
    _name = "hr.employee.participation"
    _rec_name = 'account_move_id'

    account_move_id = fields.Many2one('account.move', string="Invoice", required="True")
    currency_id = fields.Many2one(related='account_move_id.currency_id', string='Currency', store=True)
    amount_total = fields.Monetary(related='account_move_id.amount_total', string='Total', store=True, readonly=True)
    commission_type = fields.Selection(related='account_move_id.commission_type', string='Commission Type', store=True, readonly=True)
    commission_p = fields.Float(related='account_move_id.commission_p', string='Percent', store=True,
                                       readonly=True)
    commission_value_p = fields.Float(related='account_move_id.commission_value_p', string='Percent Amount', store=True, readonly=True)
    commission_value_a = fields.Float(related='account_move_id.commission_value_a', string='Amount', store=True, readonly=True)
    commission_value = fields.Float(related='account_move_id.commission_value', string='Amount', store=True,
                                      readonly=True)
    part_line_ids = fields.One2many('hr.employee.participation.line', 'part_id', string='Commission Lines')
    state = fields.Selection(selection=[
        ('disapproved', 'Disapproved'),
        ('approved', 'Approved'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='disapproved')
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid')],
        string="Payment Status", store=True, readonly=True, copy=False, compute="_compute_payment_state", default='not_paid')
    report_date = fields.Date(string='Fecha', required=True)

    _sql_constraints = [('account_uniq', 'unique (account_move_id)', 'Duplicate invoice in commission not allowed!')]

    @api.depends('part_line_ids')
    def _compute_payment_state(self):
        for rec in self:
            rec.payment_state = 'not_paid'
            if rec.part_line_ids:
                total_rec = len(rec.part_line_ids)
                total_paid = len(rec.part_line_ids.filtered(lambda t: t.paid))
                if total_rec == total_paid:
                    rec.payment_state = 'paid'

    def button_approve(self):
        self.write({'state': 'approved'})

    def button_disapprove(self):
        self.write({'state': 'disapproved'})

    @api.onchange("account_move_id")
    def _onchange_account_move_id(self):
        if self.account_move_id:
            self.report_date = self.account_move_id.invoice_date

    @api.model
    def create(self, values):
        res = super(HrEmployeeParticipation, self).create(values)
        self._check_part_percent()
        return res

    def write(self, values):
        res = super(HrEmployeeParticipation, self).write(values)
        self._check_part_percent()
        return res

    def _check_part_percent(self):
        percent_total = 0
        for line in self.part_line_ids:
            percent_total += line.part_percent

        if percent_total > 100:
            raise UserError(_("Verify the participation percent because the total (%s) can't be bigger than 100.") % percent_total)

    def unlink(self):
        for commission in self:
            if commission.state != 'disapproved':
                raise UserError("You can't delete a sale commission in Approved state.")
        return super(HrEmployeeParticipation, self).unlink()


class HrEmployeeParticipationLine(models.Model):
    _name = "hr.employee.participation.line"
    _rec_name = 'contract_id'

    part_id = fields.Many2one('hr.employee.participation', string="Participation", ondelete="cascade")
    contract_id = fields.Many2one('hr.contract', string="Contract", required="True")
    part_percent = fields.Float(string='Participation Percent', required="True")
    part_value = fields.Float(string='Participation Value')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    state = fields.Selection(related="part_id.state")
    paid = fields.Boolean(string='Paid', default=False)
    report_date = fields.Date(related="part_id.report_date")
    account_move_id = fields.Many2one(related="part_id.account_move_id")

    _sql_constraints = [('part_contract_uniq', 'unique (part_id, contract_id)',
                         'Duplicate contracts in commission lines not allowed!')]

    @api.onchange('part_percent')
    def _onchange_part_percent(self):
        if self.part_percent > 100 or self.part_percent < 0:
            self.part_percent = 0
            raise ValidationError(_('Enter value between 0-100.'))

        if self.part_id.commission_type == 'a':
            self.part_value = self.part_id.commission_value_a * self.part_percent / 100
        else:
            self.part_value = self.part_id.commission_value_p * self.part_percent / 100

