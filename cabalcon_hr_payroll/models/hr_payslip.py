# -*- coding:utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    # _sql_constraints = [
    #     (
    #     'payroll_struct_uniq', 'unique(struct_id, date_from, date_to, contract_id, state, credit_note, refund )', 'Un trabajador no pueda tener más de una nómina en un periodo y estructura salarial'
    #     ),
    # ]

    refund = fields.Boolean(string=' refund', default=False)
    details_by_salary_rule_category = fields.One2many('hr.payslip.line',
                                                      compute='_compute_details_by_salary_rule_category',
                                                      string='Details by Salary Rule Category',
                                                      help="Details from the salary rule category")

    def _compute_details_by_salary_rule_category(self):
        for payslip in self:
            payslip.details_by_salary_rule_category = payslip.mapped('line_ids').filtered(lambda line: line.category_id)

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        # res = []
        # # structure_ids = contracts.get_all_structures()
        # structure_ids = contracts.structure_type_id.struct_ids
        # rule_ids = self.env['hr.payroll.structure'].browse(structure_ids.ids).rule_ids
        # sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        # inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')
        #
        # for contract in contracts:
        #     for input in inputs:
        #         input_data = {
        #             'name': input.name,
        #             'code': input.code,
        #             'contract_id': contract.id,
        #         }
        #         res += [input_data]
        return self.input_line_ids

    def revert_leave_allocation(self):
        for payslip in self:
            holidays = self.env['hr.leave.allocation'].search([('payslip_id', '=', payslip.id)])
            holidays.action_refuse()
            holidays.action_draft()
            holidays.unlink()

    def revert_invoice(self):
        for payslip in self:
            invoice = self.env['account.move'].search([('payslip_id', '=', payslip.id)])
            invoice.button_draft()
            invoice.unlink()

    def create_leave_allocation(self):
        allocation = self.env['hr.leave.allocation']
        hs = self.env.ref('cabalcon_hr_holidays.holiday_status_vac').id
        name = "Asignación de vacaciones para %s del %s-%s" % (self.employee_id.name, self.date_from.month,self.date_from.year)
        values = {'employee_id': self.employee_id.id,
                  'holiday_type': 'employee',
                  'holiday_status_id': hs,
                  'name': name,
                  'number_of_days': 2.05,
                  'state': 'validate',
                  'payslip_id': self.id}
        allocation.create(values)

    def create_in_invoice(self):
        invoice = self.env['account.move']
        partner = self.env['res.partner'].search([('employee_id', '=', self.employee_id.id)])

        line_ids = [(0, 0, {
            'product_id':  self.company_id.product_id.id,
            'quantity': 1,
            'price_unit': self.net_wage,

        })]
        values = {'partner_id': partner.id,
                  'invoice_date': self.date_to,
                  'move_type': 'in_invoice',
                  'invoice_line_ids': line_ids,
                  'payslip_id': self.id
                  }
        invoice.sudo().create(values)

    def action_payslip_done(self):

        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_formal_independent')
        if self.employee_id.contract_id.contract_type_id == contract_type and self.net_wage > 0:
            if not self.company_id.product_id:
                raise ValidationError('Debe configurar el producto Recibo por Honorarios')
            self.create_in_invoice()

        return super(HrPayslip, self).action_payslip_done()

    def refund_sheet(self):
        for payslip in self:
            payslip.refund = True
            payslip.revert_leave_allocation()
            payslip.revert_invoice()

        return super(HrPayslip, self).refund_sheet()

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        res.update({
            'compute_employment_essalud': compute_employment_essalud,
            'compute_gratification': compute_gratification,
        })
        return res

    def _get_amount_employee_with_eps(self):
        code = 'NET'
        lines = self.line_ids.filtered(lambda line: line.code == code and line.employee_id.eps)
        return sum([line.total for line in lines])

    # Se le pasa lista de codigos de las reglas que quiere sumar y dev. el total
    def _get_salary_lines_total(self, list_of_codes):
        lines = self.line_ids.filtered(lambda line: line.code in list_of_codes)
        return sum([line.total for line in lines])

    def _action_create_account_move_byemployee(self):
        for slip in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = slip.date or slip.date_to
            current_month = date.month
            current_year = date.year
            currency = slip.company_id.currency_id

            name = _('Payslip of %s') % (slip.employee_id.name)
            reference = 'Salario {}/{} {} de {}'.format(current_month, current_year, slip.number, slip.employee_id.name)
            partner_id = False
            if slip.employee_id.address_home_id:
                partner_id = slip.employee_id.address_home_id.id
            move_dict = {
                'narration': name,
                'partner_id': partner_id,
                'ref': reference,
                'journal_id': slip.journal_id.id,
                'date': date,
            }
            for line in slip.details_by_salary_rule_category:
                amount = currency.round(slip.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,

                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': slip.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id or line.slip_id.contract_id.analytic_account_id.id,

                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if currency.compare_amounts(credit_sum, debit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                        slip.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': currency.round(debit_sum - credit_sum),
                })
                line_ids.append(adjust_credit)

            elif currency.compare_amounts(debit_sum, credit_sum) == -1:
                acc_id = slip.journal_id.default_account_id.id
                if not acc_id:
                    raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                        slip.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': currency.round(credit_sum - debit_sum),
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            move.post()
            slip.write({'move_id': move.id, 'date': date})
            print(move)
            print(move.line_ids)
            if not move.line_ids:
                raise UserError(_("As you installed the payroll accounting module you have to choose Debit and Credit"
                                  " account for at least one salary rule in the choosen Salary Structure."))
        return True

    def _action_create_account_move(self):
        by_employee = self.env.user.company_id.move_by_employee
        if by_employee:
            return self._action_create_account_move_byemployee()
        else:
            return super(HrPayslip, self)._action_create_account_move()

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        res = super(HrPayslip, self)._prepare_line_values(line, account_id, date, debit, credit)
        if line.employee_id.address_home_id and not line.slip_id.payslip_run_id:
            res['partner_id'] = line.employee_id.address_home_id.id

        return res


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    is_employer_contributions = fields.Boolean(related='salary_rule_id.is_employer_contributions', readonly=True)

    def _get_partner_id(self, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        register_partner_id = self.partner_id
        partner_id = register_partner_id.id or self.slip_id.employee_id.address_home_id.id
        if credit_account:
            if register_partner_id or self.salary_rule_id.account_credit.internal_type in ('receivable', 'payable'):
                return partner_id
        else:
            if register_partner_id or self.salary_rule_id.account_debit.internal_type in ('receivable', 'payable'):
                return partner_id
        return False


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    payslip_id = fields.Many2one('hr.payslip', string='payslip')


class AccountMove(models.Model):
    _inherit = "account.move"

    payslip_id = fields.Many2one('hr.payslip', string='payslip')


def compute_employment_essalud(payslip, categories, TOTALIMP):
    value = 0
    if payslip:
        if payslip.contract_id.employee_id.eps:
            essalud_tax = payslip.company_id.eps_tax
        else:
            essalud_tax = payslip.company_id.essalud_tax

        essalud_rmv = payslip.company_id.essalud_rmv

        net_wage = TOTALIMP

        if net_wage < essalud_rmv:
            value = essalud_rmv * essalud_tax / 100
        else:
            value = net_wage * essalud_tax / 100

    return value


def compute_gratification(payslip, categories):
    value = 0
    if payslip:
        ok = False
        if payslip.date_from.month == 7:
            date_init_str = '%s-01-01' % (payslip.date_from.year)
            date_init = fields.Date.to_date(date_init_str)
            if payslip.contract_id.date_start > date_init:
                date_init = payslip.contract_id.date_start
            date_end_str = '%s-06-30' % (payslip.date_from.year)
            date_end = fields.Date.to_date(date_end_str)
            ok = True

        if payslip.date_from.month == 12:
            date_init_str = '%s-07-01' % (payslip.date_from.year)
            date_init = fields.Date.to_date(date_init_str)
            if payslip.contract_id.date_start > date_init:
                date_init = payslip.contract_id.date_start
            date_end_str = '%s-12-31' % (payslip.date_from.year)
            date_end = fields.Date.to_date(date_end_str)
            ok = True

        if ok:
            c_months = relativedelta(date_end, date_init).months
            net_wage = categories.BASIC + payslip.AF
            value = (net_wage/6) * c_months

    return value