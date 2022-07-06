# -*- coding: utf-8 -*-
import math
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class SocialBenefits(models.Model):
    _name = 'hr.social.benefits'
    _description = 'Social benefits'

    name = fields.Char(string='Nombre')
    benefit_type = fields.Selection(string='Tipo de beneficio',
                                    selection=[('gratification', 'Gratificación'),
                                               ('cts', ' CTS'),
                                               ('liquidation', 'Liquidación')])
    gratificacion_select = fields.Selection([('FP', 'Fiestas patrias (Julio)'),
                                             ('NAV', 'Navidad (Diciembre)')],
                                            string='Gratificación')
    cts_select = fields.Selection([('CTSP1', 'CTS (Mayo)'),
                                   ('CTSP2', 'CTS (Noviembre)')],
                                  string='CTS')
    date_from = fields.Date(string='Desde', required=True,
                            default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Hasta',  required=True,
                          default=lambda self: fields.Date.to_string(
                              (datetime.now() + relativedelta(months=+6, day=1, days=-1)).date()))
    state = fields.Selection([('open', 'Abierta'),
                              ('close', 'Cerrada'),
                              ('paid', 'Pagada')],
                             string='Estado', index=True, default='open')
    report_date = fields.Date(string='Fecha de reporte', required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False, required=True,
                                 default=lambda self: self.env.company)
    gratification_ids = fields.One2many('hr.social.benefits.gratification', 'gratification_id', string='Gratificación')
    gratification_trunca_ids = fields.One2many('hr.social.benefits.gratification', 'gratification_trunca_id', string='Gratificación Truncas')
    cts_trunca_ids = fields.One2many('hr.social.benefits.gratification', 'cts_trunca_id', string='CTS Truncas')
    vacation_ids = fields.One2many('hr.social.benefits.vacations', 'social_benefits_id', string='Vacaciones Truncas')

    gratification_count = fields.Integer(compute='_compute_gratification_count', string='Gratificaciones')
    gratification_trunca_count = fields.Integer(compute='_compute_gratification_trunca_count', string='Gratificaciones truncas')
    cts_trunca_count = fields.Integer(compute='_compute_cts_trunca_count', string='CTS Trunca')
    vacation_count = fields.Integer(compute='_compute_vacation_count', string='Vacaciones')

    def _compute_gratification_count(self):
        for rec in self:
            rec.gratification_count = len(rec.gratification_ids)

    def _compute_gratification_trunca_count(self):
        for rec in self:
            rec.gratification_trunca_count = len(rec.gratification_trunca_ids)

    def _compute_cts_trunca_count(self):
        for rec in self:
            rec.cts_trunca_count = len(rec.cts_trunca_ids)

    def _compute_vacation_count(self):
        for rec in self:
            rec.vacation_count = len(rec.vacation_ids)

    def get_semester_gt(self, month):
        return math.ceil(float(month) / 6)

    def get_semester_cts(self, month):
        if month in [11, 12, 1, 2, 3, 4]:
            return 1
        else:
            return 2

    def get_period_work(self, contract, date_from, date_to):
        if date_from < contract.date_start:
            _date_from = contract.date_start
        else:
            _date_from = date_from - relativedelta(days=1)

        if contract.date_end and date_to > contract.date_end:
            _date_to = contract.date_end
        else:
            _date_to = date_to
        return _date_from, _date_to

    def cumpute_months_work(self, contract, _type=None):
        if self.benefit_type in ['gratification', 'cts']:
            date_from, date_to = self.get_period_work(contract, self.date_from, self.date_to)
        else:
            date_to = self.date_to
            cmonth = contract.date_end.month
            year = contract.date_end.year
            if _type == 'gratification':
                if self.get_semester_gt(cmonth) == 1:
                    date_from = fields.Date.from_string('%s-01-01' % year)
                else:
                    date_from = fields.Date.from_string('%s-07-01' % year)
            if _type == 'cts':
                if self.get_semester_cts(cmonth) == 1:
                    _date_from = fields.Date.from_string('%s-11-01' % (year - 1))
                else:
                    _date_from = fields.Date.from_string('%s-05-01' % year)
                date_from, date_to = self.get_period_work(contract, _date_from, contract.date_end)

        return relativedelta(date_to, date_from).months, relativedelta(date_to, date_from).days

    def cumpute_months_vacations(self, contract):
        # Año de trabajo
        validity_start = datetime.date(contract.employee_id.validity_start)
        validity_stop = datetime.date(contract.employee_id.validity_stop)
        date_from, date_to = self.get_period_work(contract, validity_start, validity_stop)

        return relativedelta(date_to, date_from).months, relativedelta(date_to, date_from).days

    def calculate(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        if self.benefit_type in ['gratification', 'cts']:
            domain = [('state', '=', 'open'), ('contract_type_id', '=', contract_type)]
            contracts = self.env['hr.contract'].sudo().search(domain)
            gratification = []
            self.gratification_ids = [(5, 0, 0)]
            for contract in contracts:
                months, days = self.cumpute_months_work(contract)
                if contract.wage_type == 'monthly':
                    wage = contract.wage
                else:
                    wage = contract.hourly_wage * 30

                if contract.is_da:
                    var_da = contract.da
                else:
                    var_da = 0

                values = [0, 0, {'employee_id': contract.employee_id.id,
                                 'contract_id': contract.id,
                                 'wage': wage,
                                 'da': var_da,
                                 'months_work': months,
                                 }]
                gratification.append(values)
            self.gratification_ids = gratification
        else:
            domain = [('state', '=', 'close'), ('contract_type_id', '=', contract_type)]
            contracts = self.env['hr.contract'].sudo().search(domain)
            gratification = []
            cts = []
            vacation = []
            self.gratification_trunca_ids = [(5, 0, 0)]
            self.cts_trunca_ids = [(5, 0, 0)]
            self.vacation_ids = [(5, 0, 0)]
            for contract in contracts:
                months, days = self.cumpute_months_work(contract, 'gratification')
                if contract.wage_type == 'monthly':
                    wage = contract.wage
                else:
                    wage = contract.hourly_wage * 30
                values = [0, 0, {'employee_id': contract.employee_id.id,
                                 'contract_id': contract.id,
                                 'wage': wage,
                                 'da': contract.da,
                                 'months_work': months,
                                 'days_work': days,
                                 }]
                gratification.append(values)
                months, days = self.cumpute_months_work(contract, 'cts')
                values = [0, 0, {'employee_id': contract.employee_id.id,
                                 'contract_id': contract.id,
                                 'wage': contract.wage,
                                 'da': contract.da,
                                 'months_work': months,
                                 'days_work': days,
                                 }]
                cts.append(values)

                months, days = self.cumpute_months_vacations(contract)
                values = [0, 0, {'employee_id': contract.employee_id.id,
                                 'contract_id': contract.id,
                                 'wage': contract.wage,
                                 'months_work': months,
                                 'da': contract.da,
                                 'days_work': days,
                                 'days_vacation': contract.employee_id.days_vacation,
                                 }]
                vacation.append(values)

            self.gratification_trunca_ids = gratification
            self.cts_trunca_ids = cts
            self.vacation_ids = vacation

    def state_close(self):
        if self.benefit_type in ['gratification', 'cts'] and not self.gratification_ids:
            raise ValidationError("No puede cerrar si aun no ha procesado la información.")
        if self.benefit_type == 'liquidation' and not self.gratification_trunca_ids:
            raise ValidationError("No puede cerrar si aun no ha procesado la información.")
        self.write({'state': 'close'})

    def state_paid(self):
        self.write({'state': 'paid'})

    def state_open(self):
        self.write({'state': 'open'})

    @api.model
    def create(self, values):
        if values['benefit_type'] == 'gratification':
            btype = 'Gratificación'
        elif values['benefit_type'] == 'cts':
            btype = 'CTS'
        else:
            btype = 'Liquidación'
        name = "{} de {} - {}".format(btype, values['date_from'], values['date_to'])
        values['name'] = name
        return super(SocialBenefits, self).create(values)

    def action_gratification(self):
        self.ensure_one()
        if self.benefit_type == 'gratification':
            btype = 'Gratificaciones'
        else:
            btype = 'CTS'

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.social.benefits.gratification",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.gratification_ids.ids]],
            "name": btype,
        }

    def action_gratification_trunca(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.social.benefits.gratification",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.gratification_trunca_ids.ids]],
            "name": 'Gratificaciones',
        }

    def action_vacations(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.social.benefits.vacations",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.vacation_ids.ids]],
            "name": 'Vacaciones',
        }

    def action_cts_trunca(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.social.benefits.gratification",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.cts_trunca_ids.ids]],
            "name": 'CTS',
        }

    def get_employees_ids(self):
        employee_ids = []
        for id in self.gratification_trunca_ids.mapped('employee_id').ids:
            employee_ids.append(id)
        for id in self.cts_trunca_ids.mapped('employee_id').ids:
            employee_ids.append(id)
        for id in self.vacation_ids.mapped('employee_id').ids:
            employee_ids.append(id)

        return list(set(employee_ids))

    def open_liquidation_wizard(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.liquidation.wizard",
            'view_mode': 'form',
            'view_id': self.env.ref('cabalcon_hr_social_benefits.hr_action_liquidation_report_wizard_view_form').id,
            "name": 'Imprimir liquidación',
            'context': {
                'social_benefit_id': self.id,
                'active_ids': self.get_employees_ids(),
            },
            'target': 'new',
        }


    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(bs.date_from > bs.date_to for bs in self):
            raise ValidationError("La fecha de inicio no puede ser mayor que la fecha fin.")

    @api.onchange('gratificacion_select')
    def _onchange_gratificacion_select(self):
        if self.gratificacion_select and self.gratificacion_select == 'FP':
            self.date_from = datetime(datetime.now().year,1,1)
            self.date_to = datetime(datetime.now().year,6,30)
            self.report_date = datetime(datetime.now().year,7,15)
        else:
            self.date_from = datetime(datetime.now().year,7,1)
            self.date_to = datetime(datetime.now().year,12,31)
            self.report_date = datetime(datetime.now().year, 12, 15)

    @api.onchange('cts_select')
    def _onchange_cts_select(self):
        if self.cts_select and self.cts_select == 'CTSP1':
            self.date_from = datetime(datetime.now().year-1,11,1)
            self.date_to = datetime(datetime.now().year,4,30)
            self.report_date = datetime(datetime.now().year, 5, 15)
        else:
            self.date_from = datetime(datetime.now().year,5,1)
            self.date_to = datetime(datetime.now().year,10,31)
            self.report_date = datetime(datetime.now().year, 11, 15)


class GratificationEmployee(models.Model):
    _name = 'hr.social.benefits.gratification'
    _description = 'Gratificaciones por empleado'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string='Contrato', readonly=True)
    wage = fields.Float('Salario Básico', compute="_compute_wage", readonly=True, store=True)
    months_work = fields.Integer(string='Meses trabajados')
    days_work = fields.Integer(string='Días trabajados')
    da = fields.Float(string="Asignación Familiar", compute="_compute_da", readonly=True, store=True)
    overtime = fields.Float(string='Horas extras')
    commissions = fields.Float(string='Comisiones')
    bonuses = fields.Float(string='Bonificaciones')
    computable_remuneration = fields.Float(string='Remuneración computable', readonly=True, compute="_cumpute_remuneration", store=True)
    amount_gratification = fields.Float(string='Gratificación', readonly=True, compute="_cumpute_amount_gratification", store=True)
    amount_gratification1_6to = fields.Float(string='Gratificación 1/6', readonly=True, compute="_cumpute_amount_gratification1_6to",
                                        store=True)

    amount_bonus = fields.Float(string='Bonificación extraordinaria', readonly=True, compute="_cumpute_amount_bonus", store=True)
    amount_total = fields.Float(string='Total', readonly=True, compute="_cumpute_amount_total", store=True)
    amount_cts = fields.Float(string='CTS', readonly=True, compute="_cumpute_amount_cts", store=True)
    gratification_id = fields.Many2one('hr.social.benefits', string='Gratification')
    gratification_trunca_id = fields.Many2one('hr.social.benefits', string='Gratification trunca')
    cts_trunca_id = fields.Many2one('hr.social.benefits', string='CTS trunca')
    benefit_type = fields.Selection(string='Tipo de beneficio',
                                    selection=[('gratification', 'Gratificación'),
                                               ('cts', ' CTS'),
                                               ('liquidation', 'Liquidación')],
                                    compute="_cumpute_benefit_type")
    cts_liquidation_date_init = fields.Date(string='Fecha de inicio del computo')

    def _compute_da(self):
        for rec in self:
            if rec.contract_id.is_af:
                rec.da = rec.contract_id.company_id.essalud_rmv * (rec.contract_id.company_id.percent_af/100)
            else:
                rec.da = 0

    def _cumpute_benefit_type(self):
        for rec in self:
            if rec.gratification_id:
                rec.benefit_type = rec.gratification_id.benefit_type
            elif rec.gratification_trunca_id:
                rec.benefit_type = rec.gratification_trunca_id.benefit_type
            else:
                rec.benefit_type = rec.cts_trunca_id.benefit_type

    @api.depends('contract_id')
    def _compute_wage(self):
        for rec in self:
            rec.wage = rec.contract_id.wage

    @api.depends('wage', 'da', 'overtime', 'commissions', 'bonuses')
    def _cumpute_remuneration(self):
        for rec in self:
            rec.computable_remuneration = rec.wage + rec.da + rec.overtime + rec.commissions + rec.bonuses

    @api.depends('computable_remuneration', 'months_work')
    def _cumpute_amount_gratification(self):
        for rec in self:
            if rec.benefit_type == 'gratification':
                rec.amount_gratification = rec.computable_remuneration / 6 * rec.months_work
            elif rec.benefit_type == 'liquidation':
                month_gratification = rec.computable_remuneration / 12 * rec.months_work
                days_gratification = rec.computable_remuneration / 12 / 30 * rec.days_work
                rec.amount_gratification = month_gratification + days_gratification
            else:
                rec.amount_gratification = 0

    @api.depends('computable_remuneration')
    def _cumpute_amount_gratification1_6to(self):
        for rec in self:
            if not rec.gratification_id.report_date:
                rec.amount_gratification1_6to = 0
            else:
                if rec.benefit_type == 'gratification':
                    rec.amount_gratification1_6to = 0
                elif rec.benefit_type == 'liquidation':
                    month_gratification = rec.computable_remuneration / 12 * rec.months_work
                    days_gratification = rec.computable_remuneration / 12 / 30 * rec.days_work
                    rec.amount_gratification1_6to = month_gratification + days_gratification
                else:
                    if isinstance(rec.gratification_id.report_date, str):
                        dte_report = fields.Date.from_string(rec.gratification_id.report_date)
                    else:
                        dte_report = rec.gratification_id.report_date
                    year = dte_report.year
                    semester = rec.gratification_id.get_semester_gt(dte_report.month)
                    # si estoy en el primer semestre de CTS buscar Gratificacion de segundo semestre del año anterior
                    if semester == 1:
                        gratification_date_from = fields.Date.from_string('%s-07-01' % (year-1))
                        gratification_date_to = fields.Date.from_string('%s-12-31' % (year-1))
                    else:
                        gratification_date_from = fields.Date.from_string('%s-01-01' % year)
                        gratification_date_to = fields.Date.from_string('%s-06-30' % year)

                    gratification = self.env['hr.social.benefits'].search([('benefit_type', '=', 'gratification'),
                                                                           ('date_from', '=', gratification_date_from),
                                                                           ('date_to', '=', gratification_date_to)],
                                                                          limit=1)
                    gratification1_6to = 0
                    if gratification:
                        employee = gratification.gratification_ids.filtered(lambda g: g.employee_id == rec.employee_id and g.contract_id == rec.contract_id)
                        if employee:
                            gratification1_6to = employee.amount_gratification/6
                    else:
                        date_from, date_to = rec.gratification_id.get_period_work(rec.contract_id, gratification_date_from,
                                                                                  gratification_date_to)
                        months_work = relativedelta(date_to, date_from).months
                        amount_gratification = rec.computable_remuneration / 6 * months_work
                        gratification1_6to = amount_gratification / 6
                    rec.amount_gratification1_6to = gratification1_6to

    @api.depends('amount_gratification')
    def _cumpute_amount_bonus(self):
        for rec in self:
            porcent = rec.employee_id.company_id.essalud_tax  # 9.0
            if rec.employee_id.eps:
                porcent = rec.employee_id.company_id.eps_tax  # 6.75
            rec.amount_bonus = rec.amount_gratification * porcent/100

    @api.depends('amount_gratification', 'amount_bonus')
    def _cumpute_amount_total(self):
        for rec in self:
            porcent = rec.contract_id.company_id.porcet_gratification
            rec.amount_total = (rec.amount_gratification + rec.amount_bonus) * porcent/100

    @api.depends('computable_remuneration', 'months_work')
    def _cumpute_amount_cts(self):
        for rec in self:
            if rec.benefit_type == 'cts':
                rec.amount_cts = rec.computable_remuneration / 12 * rec.months_work
            elif rec.benefit_type == 'liquidation':
                computable_remuneration = rec.computable_remuneration + rec.amount_gratification1_6to
                month_cts = computable_remuneration / 12 * rec.months_work
                days_cts = computable_remuneration / 12 / 30 * rec.days_work
                rec.amount_cts = month_cts + days_cts
            else:
                rec.amount_cts = 0


class VacationsEmployee(models.Model):
    _name = 'hr.social.benefits.vacations'
    _description = 'Vacaciones truncas del empleado'

    employee_id = fields.Many2one('hr.employee', string="Employee")
    contract_id = fields.Many2one('hr.contract', string='Contrato', readonly=True)
    wage = fields.Float('Salario Básico', compute="_compute_wage", readonly=True, store=True)
    months_work = fields.Integer(string='Meses trabajados')
    days_work = fields.Integer(string='Días trabajados')
    days_vacation = fields.Integer(string='Días de vacaciones')
    da = fields.Float(string="Asignación Familiar", compute="_compute_da", readonly=True, store=True)
    computable_remuneration = fields.Float(string='Remuneración computable', readonly=True, compute="_cumpute_remuneration", store=True)
    amount_vacation_trunca = fields.Float(string='Vacaciones truncas', readonly=True, compute="_cumpute_amount_vacation_truncas", store=True)
    amount_vacation = fields.Float(string='Vacaciones', readonly=True, compute="_cumpute_amount_vacation", store=True)
    social_benefits_id = fields.Many2one('hr.social.benefits', string='Gratification')

    def _compute_da(self):
        for rec in self:
            if rec.contract_id.is_af:
                rec.da = rec.contract_id.company_id.essalud_rmv * (rec.contract_id.company_id.percent_af/100)
            else:
                rec.da = 0

    @api.depends('wage', 'da')
    def _cumpute_remuneration(self):
        for rec in self:
            rec.computable_remuneration = rec.wage + rec.da

    @api.depends('computable_remuneration', 'days_vacation')
    def _cumpute_amount_vacation(self):
        for rec in self:
            month_vacation = rec.computable_remuneration / 12 * rec.days_vacation
            rec.amount_vacation = month_vacation

    @api.depends('computable_remuneration', 'months_work', 'days_work')
    def _cumpute_amount_vacation_truncas(self):
        for rec in self:
            month_vacation = rec.computable_remuneration / 12 * rec.months_work
            days_vacation = rec.computable_remuneration / 12 / 30 * rec.days_work
            rec.amount_vacation_trunca = month_vacation + days_vacation


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    gratification_ids = fields.One2many('hr.social.benefits.gratification', 'employee_id', string='Gratificaciones')
