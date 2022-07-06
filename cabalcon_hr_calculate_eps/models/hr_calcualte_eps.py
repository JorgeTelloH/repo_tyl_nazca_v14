# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError

MONTHS = [('1', 'Enero'),
          ('2', 'Febrero'),
          ('3', 'Marzo'),
          ('4', 'Abril'),
          ('5', 'Mayo'),
          ('6', 'Junio'),
          ('7', 'Julio'),
          ('8', 'Agosto'),
          ('9', 'Septiembre'),
          ('10', 'Octbre'),
          ('11', 'Noviembre'),
          ('12', 'Diciembre')]


class CalculateEPS(models.Model):
    _name = 'hr.calculate.eps'
    _description = 'Calculo del EPS'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(2021, datetime.now().year + 10, 1)]

    def get_employee_eps(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        domain = [('state', 'in', ['open','near_expire']), ('contract_type_id', '=', contract_type)]
        employees = self.env['hr.contract'].sudo().search(domain)
        ids = []
        for employee in employees.filtered(lambda c: c.employee_id.eps):
            item = [0, 0, {'employee_id': employee.employee_id.id}]
            ids.append(item)
        return ids

    name = fields.Char(string='Nombre')
    month_eps = fields.Selection(string='Mes', selection=MONTHS, required=True, default=datetime.today().month)
    year_eps = fields.Selection(string='Año', selection=_get_years, required=True, default=datetime.today().year)
    employees_quantity = fields.Integer(string='Total de empleados', compute='_compute_all_quantity', readonly=True, store=True)
    employees_quantity_eps = fields.Integer(string='Empleados afiliados a la EPS', compute='_compute_all_quantity', readonly=True, store=True)
    remuneraciones_total = fields.Float(string='Remuneraciones total', compute='_compute_all_quantity', readonly=True, store=True)
    essalud9 = fields.Float(string='9% ESSALUD', compute='_compute_all_quantity', readonly=True, store=True)
    amount1 = fields.Float(string='(1) 25 % de la norma', compute='_compute_all_quantity', readonly=True, store=True)
    uit = fields.Float(string='UIT', compute='_compute_all_quantity', readonly=True, store=True)
    uit10 = fields.Float(string='UIT 10%', compute='_compute_all_quantity', readonly=True, store=True)
    amount2 = fields.Float(string='(2) UIT*10%*#afliliados', compute='_compute_all_quantity', readonly=True, store=True)
    account_move_id = fields.Many2one('account.move', string='Factura', domain="[('move_type', '=', 'in_invoice')]")
    invoice = fields.Float(string='(3) Monto de la factura incluido IGV', required=True)
    amount_eps = fields.Float(string='Cred EPS Min(1,2,3)', compute='_compute_amount_eps', readonly=True, store=True)
    cred_amount_eps = fields.Float(string='Cred. EPS', compute='_compute_cred_amount_eps', readonly=True, store=True)
    essalud9all = fields.Float(string='9% ESSALUD todos', compute='_compute_all_quantity', readonly=True, store=True)
    pagoEmp = fields.Float(string='Pago Empleador ESSALUD', compute='_compute_all_quantity', readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Compañía', readonly=True, copy=False, required=True,
                                 default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Calculando'),
                              ('approve', 'Aprobado'),
                              ('posted', 'Publicado')],
                             string='Estado', default='draft')
    employee_ids = fields.One2many('hr.employee.eps', 'eps_id', string='Empleados', default=get_employee_eps)

    credit_account_id = fields.Many2one('account.account', string="Cta. Crédito")
    debit_account_id = fields.Many2one('account.account', string="Cta. Debito")
    journal_id = fields.Many2one('account.journal', string="Diario")
    move_id = fields.Many2one('account.move', string='Account move', required=False)

    @api.onchange('account_move_id')
    def _onchange_account_move_id(self):
        if self.account_move_id:
            self.invoice = self.account_move_id.amount_total

    def get_renumeration(self, month_eps, year_eps, employee_ids):
        date_from = fields.Date.from_string('%s-%s-01' % (year_eps, month_eps))
        date_to = date_from + relativedelta(months=+1, day=1, days=-1)
        domain = [('employee_id', 'in', employee_ids),
                  ('date_from', '>=', date_from),
                  ('date_to', '<=', date_to),
                  ('state', 'in', ['verify', 'done']),
                  ('refund', '=', False),
                  ('credit_note', '=', False)]
        amount = 0
        payslips = self.env['hr.payslip'].search(domain)
        for slip in payslips:
            amount += slip._get_salary_line_total('TOTALIMP')
        return amount

    @api.depends('month_eps', 'year_eps', 'invoice', 'employee_ids')
    def _compute_all_quantity(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        domain = [('state', 'in', ['open','near_expire']), ('contract_type_id', '=', contract_type)]
        contracts = self.env['hr.contract'].sudo().search(domain)
        contracts_eps = contracts.filtered(lambda c: c.employee_id in self.employee_ids.mapped('employee_id'))
        uit_tax = self.company_id.uit_tax
        if self.month_eps and self.year_eps:
            remuneracion = self.get_renumeration(self.month_eps, self.year_eps, self.employee_ids.mapped('employee_id').ids)
            remuneracionall = self.get_renumeration(self.month_eps, self.year_eps, contracts.mapped('employee_id').ids)
        else:
            remuneracion = 0
            remuneracionall = 0

        # Saber las Remuneraciones de todos los trabajadores y calcular el 9% ESSALUD
        if remuneracionall == 0:
            for contract in contracts:
                if contract.wage_type == 'monthly':
                    wage = contract.wage
                else:
                    wage = contract.hourly_wage * 30

                if contract.is_da:
                    var_da = contract.da
                else:
                    var_da = 0
                remuneracionall += wage + var_da

        # Saber la rmuneración de quienes tienen EPS
        if remuneracion == 0:
            for contract in contracts_eps:
                if contract.wage_type == 'monthly':
                    wage = contract.wage
                else:
                    wage = contract.hourly_wage * 30

                if contract.is_da:
                    var_da = contract.da
                else:
                    var_da = 0
                remuneracion += wage + var_da

        for rec in self:
            rec.employees_quantity = len(contracts)
            rec.employees_quantity_eps = len(self.employee_ids)
            rec.remuneraciones_total = remuneracion
            rec.essalud9 = rec.remuneraciones_total * 0.09
            rec.amount1 = rec.essalud9 * 0.25
            rec.uit = uit_tax
            rec.uit10 = uit_tax * 0.10
            rec.amount2 = (rec.employees_quantity_eps * rec.uit10)
            rec.essalud9all = remuneracionall*0.09

    @api.depends('amount1', 'amount2', 'invoice')
    def _compute_amount_eps(self):
        numeros = []
        for rec in self:
            numeros.append(rec.amount1)
            numeros.append(rec.amount2)
            if rec.invoice > 0:
                numeros.append(rec.invoice)
            numeros.sort()
            rec.amount_eps = numeros[0]
            rec.pagoEmp = rec.essalud9all - rec.amount_eps

    @api.depends('amount_eps', 'employee_ids', 'employee_ids.eps_credit')
    def _compute_cred_amount_eps(self):
        for rec in self:
            ccredi = sum([emp.eps_credit for emp in rec.employee_ids])
            if rec.amount_eps > 0 and ccredi > 0:
                if ccredi != 0:
                    rec.cred_amount_eps = rec.amount_eps / ccredi
                else:
                    rec.cred_amount_eps = rec.amount_eps
            else:
                rec.cred_amount_eps = 0

    def refresh_button(self):
        self._compute_all_quantity()

    def state_draft(self):
        self.write({'state': 'draft'})

    def state_approve(self):
        if not self.debit_account_id or not self.credit_account_id or not self.journal_id:
            raise ValidationError("Debe especificar la información para la contabilidad")

        if self.move_id:
            _move = self.env['account.move'].sudo().browse(self.move_id.id)
            _move.unlink()

        timenow = time.strftime('%Y-%m-%d')
        amount = self.amount_eps
        eps_name = self.month_eps + "/" + self.year_eps
        reference = eps_name
        journal_id = self.journal_id.id
        debit_account_id = self.debit_account_id.id
        credit_account_id = self.credit_account_id.id
        debit_vals = {
            'name': eps_name,
            'account_id': debit_account_id,
            'journal_id': journal_id,
            'date': timenow,
            'debit': amount > 0.0 and amount or 0.0,
            'credit': amount < 0.0 and -amount or 0.0,
            'eps_id': self.id,
        }
        credit_vals = {
            'name': eps_name,
            'account_id': credit_account_id,
            'journal_id': journal_id,
            'date': timenow,
            'debit': amount < 0.0 and -amount or 0.0,
            'credit': amount > 0.0 and amount or 0.0,
            'eps_id': self.id,
        }
        vals = {
            'name': 'EPS For' + ' ' + eps_name,
            'narration': eps_name,
            'ref': reference,
            'journal_id': journal_id,
            'date': timenow,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }
        move = self.env['account.move'].sudo().create(vals)
        self.move_id = move
        # move.post()

        for rec in self.employee_ids:
            eps_vals = {
                'eps_amount_plan': rec.eps_amount_plan,
                'eps_amount': rec.eps_amount,
                'eps_credit': rec.eps_credit,
                'eps_credit_employer': rec.eps_credit_employer,
            }
            rec.employee_id.write(eps_vals)

        if self.company_id:
            self.company_id.eps_credit_amount = self.amount_eps
        self.write({'state': 'approve'})

    def state_posted(self):
        if self.move_id:
            self.move_id.post()
            self.write({'state': 'posted'})

    @api.model
    def create(self, values):
        description_values = {elem[0]: elem[1] for elem in self._fields['month_eps']._description_selection(self.env)}
        mes = description_values.get(values['month_eps'])
        name = "EPS de {} - {}".format(mes, values['year_eps'])
        values['name'] = name
        return super(CalculateEPS, self).create(values)

    def unlink(self):
        for eps in self:
            if eps.state == 'approve':
                raise ValidationError("No esta permitido borrar un cálculo de EPS si ya esta aprobado")
        return super(CalculateEPS, self).unlink()


class HrEmployeeEps(models.Model):
    _name = 'hr.employee.eps'
    _description = 'EPS por Empleado'

    eps_id = fields.Many2one('hr.calculate.eps', string='EPS')
    employee_id = fields.Many2one('hr.employee', string='Empleado')
    eps_amount_plan = fields.Float(string='Plan EPS', related='employee_id.eps_amount_plan', readonly=False)
    eps_credit = fields.Integer(string='Cantidad de credito EPS', related='employee_id.eps_credit', readonly=False)
    eps_credit_employer = fields.Integer(string='Creditos asumidos por el empleador', related='employee_id.eps_credit_employer', readonly=False)
    eps_amount = fields.Float(string='Importe EPS', compute='_compute_eps_amount', store=True, readonly=True)
    eps_amount_employee = fields.Float(string='Aporte del empleado', related='employee_id.eps_amount_employee', readonly=False)
    eps_amount_employer = fields.Float(string='Aporte del empleador', related='employee_id.eps_amount_employer', readonly=False)

    @api.depends('eps_credit', 'eps_id.cred_amount_eps','eps_amount_employer','eps_amount_plan')
    def _compute_eps_amount(self):
        for rec in self:
            rec.eps_amount = rec.eps_id.cred_amount_eps * rec.eps_credit
            #si los creditos del empleado son cero es que todo lo paga el empleador
            if rec.eps_credit == 0:
                rec.eps_amount_employer = rec.eps_amount_plan
            else:
                # si el empleador paga todo el EPS que el empleado pague los creditos que no pague el empleador
                rec.eps_amount_employee = rec.eps_amount_plan - rec.eps_id.cred_amount_eps * (rec.eps_credit - rec.eps_credit_employer)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            employee = self.env['hr.employee'].browse(self.employee_id.id)
            employee.write({'eps': True})

    def unlink(self):
        for _eps in self:
            employee = self.env['hr.employee'].browse(_eps.employee_id.id)
            employee.write({'eps': False})

        return super(HrEmployeeEps, self).unlink()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    eps_id = fields.Many2one('hr.calculate.eps', 'EPS Id')
