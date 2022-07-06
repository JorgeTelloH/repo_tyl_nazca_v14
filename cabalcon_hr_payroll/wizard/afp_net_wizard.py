# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AfpNetWizard(models.TransientModel):
    _name = 'afp.net.wizard'

    option = fields.Selection(string='Optción',
                              selection=[('week', 'Semanal'),
                                         ('month', 'Mensual'), ],
                              required=True, default='week')

    week_id = fields.Many2one('contributive.week', string='Semana')
    date_from = fields.Date(string='Fecha de inicio', required=True)
    date_to = fields.Date(string='Fecha fin', required=True)
    confirm = fields.Boolean(string='Confirmada', default=True)
    show_header = fields.Boolean(string='Mostrar encabezado de columnas', default=True)

    @api.onchange('option')
    def onchange_option(self):
        if self.option and self.option == 'month':
            self.date_from = fields.Date.today().replace(day=1)

    @api.onchange('week_id')
    def onchange_week_id(self):
        if self.week_id:
            self.date_from = self.week_id.week_from
            self.date_to = self.week_id.week_to

    @api.onchange('date_from')
    def onchange_date_from(self):
        if self.date_from and self.option == 'month':
            self.date_to = self.date_from + relativedelta(months=+1, day=1, days=-1)

    def action_print(self):
        if self.date_to < self.date_from:
            raise ValidationError('La fecha fin no puede ser menor que la fecha inicio')

        contract_type = self.env.ref('cabalcon_hr.hr_contract_type_dependent').id
        # employees = self.env['hr.employee'].search([('contract_id.contract_type_id', '=', contract_type), ('regimen_pensions', '=', 'afp')])

        domain = [
            ('contract_id.contract_type_id', '=', contract_type),
            ('employee_id.regimen_pensions', '=', 'afp'),
            ('refund', '=', False),
            ('credit_note', '=', False),
            ('date_from', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
        ]
        if self.confirm:
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '!=', 'cancel')]

        employees = self.env['hr.payslip'].search(domain).mapped('employee_id')

        if not employees:
            raise ValidationError('No se encontraron empleados para este reporte')

        data = {'data_report': employees.ids, 'show_header': self.show_header, 'date_from': self.date_from,
                'date_to': self.date_to, 'week': self.week_id.week, 'confirm': self.confirm}
        if self.option == 'month':
            return self.env.ref('cabalcon_hr_payroll.action_afp_net_report_xlsx').report_action(self, data=data)
        else:
            return self.env.ref('cabalcon_hr_payroll.action_afp_net_week_report_xlsx').report_action(self, data=data)
