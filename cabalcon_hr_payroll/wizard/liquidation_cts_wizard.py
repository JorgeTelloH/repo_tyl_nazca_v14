# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
# ------------------------------------------------------------------------------------
# ESTO YA NO SE DEBE USAR, EL MODULO CABALCON_HR_SOCIAL_BENEFITS YA HACE ESTOS CALCULOS
# ------------------------------------------------------------------------------------


class HrLiquidationCTSWizard(models.TransientModel):
    _name = 'hr.liquidation.cts.wizard'

    def _get_default_date_from(self):
        if 1 <= fields.Date.today().month <= 6:
            str_date = '{}-01-01'.format(fields.Date.today().year)
        else:
            str_date = '{}-07-01'.format(fields.Date.today().year)
        return str_date

    def _get_default_date_to(self):
        if 1 <= fields.Date.today().month <= 6:
            str_date = '{}-06-30'.format(fields.Date.today().year)
        else:
            str_date = '{}-12-31'.format(fields.Date.today().year)
        return str_date

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.context.get('active_id', None))
    date_from = fields.Date(string='Fecha inicio', required=True, default=_get_default_date_from)
    date_to = fields.Date(string='Fecha fin', required=True, default=_get_default_date_to)
    date_deposit = fields.Date(string='Fecha del deposito', required=True, default=fields.Date.today())
    bonuses = fields.Monetary(string='Bonificaciones')
    commissions = fields.Monetary(string='Comisiones (promedio semestral)')
    overtime_average = fields.Monetary(string='Horas Extras (promedio semestral)')
    average_gratification = fields.Monetary(string='Gratificaciones (dozavos, sextos o promedio)')
    other = fields.Monetary(string='Otros conceptos percibidos regularmente')
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)

    def _compute_months_and_days(self, date_from, date_to):
        months = 0
        days = 0
        if date_from and date_to:
            months = relativedelta(date_to, date_from).months
            days = relativedelta(date_to, date_from).days
        return months, days

    def action_print(self):
        self.ensure_one()
        employee = self.employee_id

        months, days = self._compute_months_and_days(self.date_from, self.date_to)

        datas = {'date_from': self.date_from.strftime('%d/%m/%Y'), 'date_to': self.date_to.strftime('%d/%m/%Y'), 'bonuses': self.bonuses,
                 'commissions': self.commissions, 'overtime_average': self.overtime_average,
                 'average_gratification': self.average_gratification, 'other': self.other,
                 'months': months, 'days': days, 'date_deposit': employee.get_date_to_report(self.date_deposit)}

        return self.env.ref('cabalcon_hr_payroll.action_liquidation_cts_report').report_action(employee, data=datas)
