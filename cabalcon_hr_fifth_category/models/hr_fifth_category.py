# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, _, api
from odoo.exceptions import ValidationError


class FifthCategory(models.Model):
    _name = 'hr.fifth.category'
    _description = 'Fifth category'

    def set_domain(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        domain = [('state', 'in', ['open', 'near_expire']), ('contract_type_id', '=', contract_type)]
        active_ids = self.env['hr.contract'].sudo().search(domain).mapped('employee_id').ids
        return [('id', 'in', active_ids)]

    def set_date_from(self):
        _date = fields.Date.to_string(date.today().replace(day=1, month=1))
        fifth = self.env['hr.fifth.category'].search([('date_from', '>=', _date)], limit=1, order='date_from DESC')
        if fifth:
            return fifth.date_from + relativedelta(months=+1, day=1)
        else:
            return _date

    name = fields.Char(string='Nombre')
    date_from = fields.Date(string='Desde', required=True,
                            default=set_date_from)
    date_to = fields.Date(string='Hasta', required=True,
                          default=lambda self: fields.Date.to_string(date.today().replace(day=31, month=12)))
    renta_year = fields.Char(string='Year')
    state = fields.Selection([('open', 'Abierta'),
                              ('close', 'Cerrada'),
                              ('paid', 'Pagada')],
                             string='Estado', index=True,
                             default='open')

    option = fields.Selection(string='Opción',
                              selection=[('all', 'Todos'),
                                         ('selectd', 'Los seleccionados')],
                              default='all')
    employee_ids = fields.Many2many('hr.employee', string='Empleados', domain=set_domain)
    struct_id = fields.Many2one('hr.payroll.structure', string="Estructura salarial", required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False, required=True,
                                 default=lambda self: self.env.company)
    lines_ids = fields.One2many('hr.fifth.category.lines', 'category_id', string='Renta de quinta')
    lines_count = fields.Integer(compute='_compute_lines_count', string='Quinta')

    @api.onchange('date_from')
    def _onchange_date_from(self):
        self.renta_year = self.date_from.year
        print('año....',self.renta_year)

    def _compute_lines_count(self):
        for rec in self:
            rec.lines_count = len(rec.lines_ids)

    def compute_maximum_deductible(self):
        uit_tax = self.company_id.uit_tax
        uit_7 = 7
        amount_maximum_deductible = uit_7 * uit_tax
        return amount_maximum_deductible

    # Gratificación Percibidas en el mes
    def get_gratification_of_july(self, year, current_month, contract):
        # buscar en la grtificación de julio
        if current_month == 8:
            date_from = fields.Date.from_string('%s-%s-01' % (year, 7))
            date_to = date_from + relativedelta(months=+1, day=1, days=-1)
            employee_id = contract.employee_id.id
            domain = [('employee_id', '=', employee_id),
                      ('date_from', '>=', date_from),
                      ('date_to', '<=', date_to),
                      ('state', '=', 'done'),
                      ('refund', '=', False),
                      ('credit_note', '=', False),
                      ('struct_id', '=', self.struct_id.id)]
            payslip = self.env['hr.payslip'].search(domain)
            if payslip:
                # TODO Agregar los codigos que falten
                value = payslip._get_salary_lines_total(['BS_GRATIF'])
                return value
            else:
                # Buscar en la ultima renta el salario
                field_name = 'computable_remuneration'
                sql = """SELECT %s
                         FROM hr_fifth_category AS fc
                         INNER JOIN hr_fifth_category_lines AS fcl ON fcl.category_id = fc."id"
                         WHERE fcl.employee_id = %s and extract(MONTH FROM date_from) <= %s
                         ORDER BY date_from DESC LIMIT 1 """ % (field_name, contract.employee_id.id, current_month)
                self._cr.execute(sql)
                result = self._cr.dictfetchone()
                wage_month = 0
                if result:
                    wage_month = result.get(field_name) or 0
                    tax = 1 + contract.employee_id.company_id.essalud_tax / 100
                    if contract.employee_id.eps:
                        tax = 1 + contract.employee_id.company_id.eps_tax / 100
                    wage_month = wage_month * tax
                return wage_month
        else:
            return 0

    # Remuneraciones Percibidas en el mes
    def get_wage_of_month(self, year, current_month, contract, field):
        _month = current_month - field
        if _month == 1 or current_month > field:
            # buscar en la nomina el salario del mes
            date_from = fields.Date.from_string('%s-%s-01' % (year, field))
            date_to = date_from + relativedelta(months=+1, day=1, days=-1)
            employee_id = contract.employee_id.id
            domain = [('employee_id', '=', employee_id),
                      ('date_from', '>=', date_from),
                      ('date_to', '<=', date_to),
                      ('state', '=', 'done'),
                      ('refund', '=', False),
                      ('credit_note', '=', False),
                      ('struct_id', '=', self.struct_id.id)]
            payslip = self.env['hr.payslip'].search(domain)
            if payslip:
                # TODO Agregar los codigos que falten
                value = payslip._get_salary_lines_total(['BASIC', 'AF', 'OVERTIME-25', 'OVERTIME-35', 'COMM'])
                return value
            else:
                # Buscar en la ultima renta el salario en el calculo anterior
                field_name = 'computable_remuneration'
                sql = """SELECT %s
                         FROM hr_fifth_category AS fc
                         INNER JOIN hr_fifth_category_lines AS fcl ON fcl.category_id = fc."id"
                         WHERE fcl.employee_id = %s and extract(MONTH FROM date_from) <= %s
                         ORDER BY date_from DESC LIMIT 1 """ % (field_name, contract.employee_id.id, field)
                self._cr.execute(sql)
                result = self._cr.dictfetchone()
                wage_month = 0
                if result:
                    wage_month = result.get(field_name) or 0
                return wage_month
        else:
            return 0

    # Retenciones en el mes
    def get_retention_of_month(self, current_month, contract, field):
        _month = current_month - field
        if _month == 1 or current_month > field:
            sql = """SELECT monthly_retention
                     FROM hr_fifth_category AS fc
                     INNER JOIN hr_fifth_category_lines AS fcl ON fcl.category_id = fc."id"
                     WHERE fcl.employee_id = %s and extract(MONTH FROM date_from) <= %s
                     order by date_from DESC LIMIT 1 """ % (contract.employee_id.id, field)
            self._cr.execute(sql)
            result = self._cr.dictfetchone()
            monthly_retention = 0
            if result:
                monthly_retention = result.get('monthly_retention') or 0
            return monthly_retention
        else:
            return 0

    def calculate(self):
        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        _date = self.date_from + relativedelta(months=+1, day=1, days=-1)
        domain = [('state', 'in', ['open', 'near_expire']),
                  ('contract_type_id', '=', contract_type),
                  ('date_start', '<', str(_date))]
        if self.option == 'selectd':
            domain += [('employee_id', 'in', self.employee_ids.ids)]
        contracts = self.env['hr.contract'].sudo().search(domain)

        uit_tax = self.company_id.uit_tax
        amount_maximum_deductible = self.compute_maximum_deductible()
        renta = []
        var_month = self.date_from.month
        var_year = self.date_from.year
        # self.lines_ids = [(5, 0, 0)]
        for contract in contracts:
            result = self.env['hr.fifth.category.lines'].search([('category_id', '=', self.id),
                                                                 ('employee_id', '=', contract.employee_id.id),
                                                                 ('contract_id', '=', contract.id)])
            if contract.wage_type == 'monthly':
                wage = contract.wage
            else:
                wage = contract.hourly_wage * 30

            if contract.is_da:
                var_da = contract.da
            else:
                var_da = 0

            values = {'employee_id': contract.employee_id.id,
                      'contract_id': contract.id,
                      'wage': wage,
                      'da': var_da,
                      'overtime': 0,
                      'amount_other_remuneration': 0,
                      'uit_tax': uit_tax,
                      'wage_month_1': self.get_wage_of_month(var_year, var_month, contract, 1),
                      'wage_month_2': self.get_wage_of_month(var_year, var_month, contract, 2),
                      'wage_month_3': self.get_wage_of_month(var_year, var_month, contract, 3),
                      'wage_month_4': self.get_wage_of_month(var_year, var_month, contract, 4),
                      'wage_month_5': self.get_wage_of_month(var_year, var_month, contract, 5),
                      'wage_month_6': self.get_wage_of_month(var_year, var_month, contract, 6),
                      'wage_month_7': self.get_wage_of_month(var_year, var_month, contract, 7),
                      'wage_month_8': self.get_wage_of_month(var_year, var_month, contract, 8),
                      'wage_gratification_jul': self.get_gratification_of_july(var_year, var_month, contract),
                      'wage_month_9': self.get_wage_of_month(var_year, var_month, contract, 9),
                      'wage_month_10': self.get_wage_of_month(var_year, var_month, contract, 10),
                      'wage_month_11': self.get_wage_of_month(var_year, var_month, contract, 11),
                      'retention_month_1': self.get_retention_of_month(var_month, contract, 1),
                      'retention_month_2': self.get_retention_of_month(var_month, contract, 2),
                      'retention_month_3': self.get_retention_of_month(var_month, contract, 3),
                      'retention_month_4': self.get_retention_of_month(var_month, contract, 4),
                      'retention_month_5': self.get_retention_of_month(var_month, contract, 5),
                      'retention_month_6': self.get_retention_of_month(var_month, contract, 6),
                      'retention_month_7': self.get_retention_of_month(var_month, contract, 7),
                      'retention_month_8': self.get_retention_of_month(var_month, contract, 8),
                      'retention_month_9': self.get_retention_of_month(var_month, contract, 9),
                      'retention_month_10': self.get_retention_of_month(var_month, contract, 10),
                      'retention_month_11': self.get_retention_of_month(var_month, contract, 11),
                      'amount_maximum_deductible': amount_maximum_deductible,
                      }

            if not result:
                item = [0, 0, values]
                renta.append(item)
        if renta:
            self.lines_ids = renta

    def state_close(self):
        if not self.lines_ids:
            raise ValidationError("No puede cerrar si aún no ha procesado la información.")

        for item in self.lines_ids:
            contract = self.env['hr.contract'].sudo().browse(item.contract_id.id)
            contract.write({'produce_5ta_category': item.monthly_retention})
        self.write({'state': 'close'})

    def state_paid(self):
        self.write({'state': 'paid'})

    def state_open(self):
        self.write({'state': 'open'})

    @api.model
    def create(self, values):
        name = "{} de {} - {}".format('Renta de quinta categoría', values['date_from'], values['date_to'])
        values['name'] = name
        return super(FifthCategory, self).create(values)

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if any(bs.date_from > bs.date_to for bs in self):
            raise ValidationError("La fecha de inicio no puede ser mayor que la fecha fin.")

    def action_open_fifth_category(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "hr.fifth.category.lines",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.lines_ids.ids]],
            "name": "Renta 5ta Cat.",
        }

    def unlink(self):
        for fifth in self:
            if fifth.state != 'open':
                raise ValidationError("No esta permitido borrar la Renta de 5ta. si ya esta cerrada")
        return super(FifthCategory, self).unlink()


class FifthCategoryLines(models.Model):
    _name = 'hr.fifth.category.lines'
    _description = 'Renta de 5tq categoría por empleado'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Empleado", readonly=True)
    contract_id = fields.Many2one('hr.contract', string='Contracto', readonly=True)

    wage = fields.Float(string='Remuneración Mensual')
    da = fields.Float(string="Asignación Familiar", readonly=True, help="Asignación Familiar")
    overtime = fields.Float(string='Horas extras')
    computable_remuneration = fields.Float('Remuneración computable', readonly=True, compute="_computable_remuneration",
                                           store=True)
    gratification_jul = fields.Float('Gratificación Julio', readonly=True, compute="_cumpute_amount_gratification",
                                     store=True)
    gratification_dic = fields.Float('Gratificación Diciembre', readonly=True, compute="_cumpute_amount_gratification",
                                     store=True)
    bonus = fields.Float('Bonificación Extraordinaria')
    amount_another_companies = fields.Float('Total percibido en otras empresas')
    amount_utilities = fields.Float('Participación en las utilidades')
    amount_other_remuneration = fields.Float('Otras remuneraciones')

    wage_month = fields.Float(string='Total mes', compute='_compute_wage_month', store=True)
    remuneration = fields.Float(string='Proyección de ingresos brutos anuales', compute='_compute_remuneration')

    total_remuneration = fields.Float('Total remuneraciones', compute='_compute_total_remuneration', store=True)
    uit_tax = fields.Float(string='UIT', readonly=True)
    amount_maximum_deductible = fields.Float(string='Máximo deducible', readonly=True)
    net_taxable_income = fields.Float(string='Renta neta imponible', readonly=True,
                                      compute='_compute_net_taxable_income', store=True)

    amount_uit_from_1 = fields.Float('Desde UIT 1', compute='_compute_uit', readonly=True)
    amount_uit_to_1 = fields.Float('Hasta UIT 1', compute='_compute_uit', readonly=True)
    amount_tax_1 = fields.Float('Hasta 5 UIT', compute='_compute_tax', store=True, readonly=True)

    amount_uit_from_2 = fields.Float('Desde UIT 2', compute='_compute_uit', readonly=True)
    amount_uit_to_2 = fields.Float('Hasta UIT 2', compute='_compute_uit', readonly=True)
    amount_tax_2 = fields.Float('Más de 5 UIT hasta 20 UIT', compute='_compute_tax', store=True, readonly=True)

    amount_uit_from_3 = fields.Float('Desde UIT 3', compute='_compute_uit', readonly=True)
    amount_uit_to_3 = fields.Float('Hasta UIT 3', compute='_compute_uit', readonly=True)
    amount_tax_3 = fields.Float('Más de 20 UIT hasta 35 UIT', compute='_compute_tax', store=True, readonly=True)

    amount_uit_from_4 = fields.Float('Desde UIT 4', compute='_compute_uit', readonly=True)
    amount_uit_to_4 = fields.Float('Hasta UIT 4', compute='_compute_uit', readonly=True)
    amount_tax_4 = fields.Float('Más de 35 UIT hasta 45 UIT', compute='_compute_tax', store=True, readonly=True)

    amount_uit_from_5 = fields.Float('Desde UIT 5', compute='_compute_uit', readonly=True)
    amount_uit_to_5 = fields.Float('Hasta UIT 5', compute='_compute_uit', readonly=True)
    amount_tax_5 = fields.Float('Más de 45 UIT', compute='_compute_tax', store=True, readonly=True)
    # Remuneraciones Percibidas
    wage_month_1 = fields.Float('Enero')
    wage_month_2 = fields.Float('Febrero')
    wage_month_3 = fields.Float('Marzo')
    wage_month_4 = fields.Float('Abril')
    wage_month_5 = fields.Float('Mayo')
    wage_month_6 = fields.Float('Junio')
    wage_gratification_jul = fields.Float('Gratificación Julio')
    wage_month_7 = fields.Float('Julio')
    wage_month_8 = fields.Float('Agosto')
    wage_month_9 = fields.Float('Septiembre')
    wage_month_10 = fields.Float('Obtubre')
    wage_month_11 = fields.Float('Noviembre')
    before_remuneration = fields.Float('Remuneraciones anteriores', compute='_compute_before_remuneration')
    # Rentenciones Anteriores
    retention_month_1 = fields.Float('Enero')
    retention_month_2 = fields.Float('Febrero')
    retention_month_3 = fields.Float('Marzo')
    retention_month_4 = fields.Float('Abril')
    retention_month_5 = fields.Float('Mayo')
    retention_month_6 = fields.Float('Junio')
    retention_month_7 = fields.Float('Julio')
    retention_month_8 = fields.Float('Agosto')
    retention_month_9 = fields.Float('Septiembre')
    retention_month_10 = fields.Float('Obtubre')
    retention_month_11 = fields.Float('Noviembre')
    before_retention = fields.Float('Rentenciones Anteriores', compute='_compute_before_retention')

    amount_tax = fields.Float('Impuesto a la Renta a pagar por el año en curso', compute='_compute_amount_tax',
                              store=True, readonly=True)

    retained_tax_another_companies = fields.Float(string='Impuesto retenido por otras empresas')
    retained_tax_in_excess = fields.Float(string='Impuesto retenido en exceso (devolución)')
    total_retained_tax = fields.Float(string='Impuesto total retenido', compute='_compute_total_retained_tax',
                                      readonly=True)
    taxable_income_retain = fields.Float(string='Renta Imponible por Retener', compute='_compute_taxable_income_retain')

    monthly_retention = fields.Float(string='Retención Mensual', compute='_compute_monthly_retention', readonly=True,
                                     store=True)

    category_id = fields.Many2one('hr.fifth.category', string='Gratification')

    @api.depends('wage', 'da', 'overtime', 'gratification_jul', 'gratification_dic', 'bonus',
                 'amount_another_companies', 'amount_utilities', 'amount_other_remuneration')
    def _compute_wage_month(self):
        for rec in self:
            rec.wage_month = rec.wage + rec.da + rec.overtime + rec.gratification_jul + rec.gratification_dic + rec.bonus + rec.amount_another_companies + rec.amount_utilities + rec.amount_other_remuneration

    def _compute_remuneration(self):
        for rec in self:
            if rec.category_id.date_from:
                _month = 12 - int(rec.category_id.date_from.month)
            else:
                _month = 12
            rec.remuneration = (rec.wage + rec.da) * _month

    @api.depends('remuneration', 'wage_month', 'before_remuneration')
    def _compute_total_remuneration(self):
        for rec in self:
            rec.total_remuneration = rec.remuneration + rec.wage_month + rec.before_remuneration

    @api.depends('wage_month_1', 'wage_month_2', 'wage_month_3', 'wage_month_4', 'wage_month_5', 'wage_month_6',
                 'wage_month_7', 'wage_month_8', 'wage_month_9', 'wage_month_10', 'wage_month_11',
                 'wage_gratification_jul')
    def _compute_before_remuneration(self):
        for rec in self:
            rec.before_remuneration = rec.wage_month_1 + rec.wage_month_2 + rec.wage_month_3 + rec.wage_month_4 + rec.wage_month_5 + rec.wage_month_6 + rec.wage_month_7 + rec.wage_month_8 + rec.wage_month_9 + rec.wage_month_10 + rec.wage_month_11 + rec.wage_gratification_jul

    @api.depends('retention_month_1', 'retention_month_2', 'retention_month_3', 'retention_month_4',
                 'retention_month_5', 'retention_month_6',
                 'retention_month_7', 'retention_month_8', 'retention_month_9', 'retention_month_10',
                 'retention_month_11')
    def _compute_before_retention(self):
        for rec in self:
            rec.before_retention = rec.retention_month_1 + rec.retention_month_2 + rec.retention_month_3 + rec.retention_month_4 + rec.retention_month_5 + rec.retention_month_6 + rec.retention_month_7 + rec.retention_month_8 + rec.retention_month_9 + rec.retention_month_10 + rec.retention_month_11

    @api.depends('total_remuneration', 'amount_maximum_deductible')
    def _compute_net_taxable_income(self):
        for rec in self:
            income = rec.total_remuneration - rec.amount_maximum_deductible
            if income > 0:
                rec.net_taxable_income = income
            else:
                rec.net_taxable_income = 0

    @api.depends('net_taxable_income', 'total_remuneration', 'amount_maximum_deductible')
    def _compute_tax(self):
        for rec in self:
            uit_tax = rec.uit_tax
            net_taxable_income = rec.net_taxable_income
            total_remuneration = rec.total_remuneration
            amount_maximum_deductible = rec.amount_maximum_deductible
            tax1 = self.env.ref('cabalcon_hr_fifth_category.tax_1')
            max1 = uit_tax * tax1.uit_to
            if total_remuneration < amount_maximum_deductible:
                afecto1 = 0
            else:
                if max1 <= net_taxable_income:
                    afecto1 = max1
                else:
                    afecto1 = net_taxable_income
            resto1 = net_taxable_income - afecto1
            rec.amount_tax_1 = afecto1 * tax1.tax / 100

            tax2 = self.env.ref('cabalcon_hr_fifth_category.tax_2')
            max2 = uit_tax * tax2.uit_to
            if (max2 - afecto1) <= resto1:
                afecto2 = max2 - afecto1
            else:
                afecto2 = resto1
            resto2 = resto1 - afecto2
            rec.amount_tax_2 = afecto2 * tax2.tax / 100

            tax3 = self.env.ref('cabalcon_hr_fifth_category.tax_3')
            max3 = uit_tax * tax3.uit_to
            if max3 - afecto2 - afecto1 <= resto2:
                afecto3 = max3 - afecto2 - afecto1
            else:
                afecto3 = resto2
            resto3 = resto2 - afecto3
            rec.amount_tax_3 = afecto3 * tax3.tax / 100

            tax4 = self.env.ref('cabalcon_hr_fifth_category.tax_4')
            max4 = uit_tax * tax4.uit_to
            if max4 - afecto3 - afecto2 - afecto1 <= resto3:
                afecto4 = max3 - afecto3 - afecto2 - afecto1
            else:
                afecto4 = resto3
            resto4 = resto3 - afecto4
            rec.amount_tax_4 = afecto4 * tax4.tax / 100

            tax5 = self.env.ref('cabalcon_hr_fifth_category.tax_5')
            if rec.net_taxable_income > max4:
                afecto5 = net_taxable_income - max4
            else:
                afecto5 = 0
            rec.amount_tax_5 = afecto5 * tax5.tax / 100

    @api.depends('amount_tax_1', 'amount_tax_2', 'amount_tax_3', 'amount_tax_4', 'amount_tax_5')
    def _compute_amount_tax(self):
        for rec in self:
            rec.amount_tax = rec.amount_tax_1 + rec.amount_tax_2 + rec.amount_tax_3 + rec.amount_tax_4 + rec.amount_tax_5

    def _compute_uit(self):
        taxs = self.env['hr.fifth.category.tax'].search([])
        for rec in self:
            uit_tax = rec.contract_id.company_id.uit_tax
            for i, tax in enumerate(taxs, start=1):
                _field_from = 'amount_uit_from_%s' % i
                _field_to = 'amount_uit_to_%s' % i
                rec[_field_from] = uit_tax * tax.uit_from
                rec[_field_to] = uit_tax * tax.uit_to

    @api.depends('retained_tax_another_companies', 'amount_tax', 'retained_tax_in_excess', 'before_retention')
    def _compute_total_retained_tax(self):
        for rec in self:
            rec.total_retained_tax = rec.retained_tax_another_companies + rec.amount_tax - rec.retained_tax_in_excess - rec.before_retention

    @api.depends('before_retention', 'total_retained_tax')
    def _compute_taxable_income_retain(self):
        for rec in self:
            rec.taxable_income_retain = rec.total_retained_tax - rec.before_retention

    @api.depends('before_retention', 'bonus', 'amount_another_companies', 'amount_utilities',
                 'amount_other_remuneration')
    def _compute_monthly_retention(self):
        for rec in self:
            if rec.category_id and rec.category_id.date_from:
                _month = 12 - (int(rec.category_id.date_from.month) - 1)  # Meses Pendientes por Retener
                rec.monthly_retention = rec.total_retained_tax / _month
            else:
                rec.monthly_retention = 0

    def get_amount_to_text(self, value):
        currency = self.contract_id.company_id.currency_id
        return currency.amount_to_text(value)

    @api.depends('wage', 'da', 'overtime', 'bonus')
    def _computable_remuneration(self):
        for rec in self:
            rec.computable_remuneration = rec.wage + rec.da + rec.overtime + rec.bonus

    @api.depends('computable_remuneration')
    def _cumpute_amount_gratification(self):
        for rec in self:
            tax = 1 + rec.employee_id.company_id.essalud_tax / 100
            if rec.employee_id.eps:
                tax = 1 + rec.employee_id.company_id.eps_tax / 100
            if int(rec.category_id.date_from.month) < 8:
                rec.gratification_jul = rec.computable_remuneration * tax
            rec.gratification_dic = rec.computable_remuneration * tax

    def unlink(self):
        for fifth in self:
            if fifth.category_id.state != 'open':
                raise ValidationError("No esta permitido borrar la Renta de 5ta. si ya esta cerrada")
        return super(FifthCategoryLines, self).unlink()


class FifthCategoryTax(models.Model):
    _name = 'hr.fifth.category.tax'
    _description = 'Impuestos a la renta'

    name = fields.Char(string='Escala UIT', required=True)
    tax = fields.Float(string='Tasa %', required=True)
    uit_from = fields.Integer(string='Desde')
    uit_to = fields.Integer(string='Hasta')
