# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
# ------------------------------------------------------------------------------------
# ESTO YA NO SE DEBE USAR, EL MODULO CABALCON_HR_SOCIAL_BENEFITS YA HACE ESTOS CALCULOS
# ------------------------------------------------------------------------------------


class HrLiquidationWizard(models.TransientModel):
    _name = 'hr.liquidation.wizard'

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True,
                                  default=lambda self: self.env.context.get('active_id', None))
    date_init = fields.Date(string='Fecha de Inicio de Computo', required=True,
                            default=lambda self: self.env.context.get('liquidation_date', None))
    average_gratification = fields.Float(string='Promedio Gratificación', required=True,
                                         default=lambda self: self.env.context.get('average_gratification', 0))
    overtime_average = fields.Float(string='Horas Extras (Promedio)', required=True,
                                    default=lambda self: self.env.context.get('overtime_average', 0))

    cut_vacations = fields.Integer(string='Periodo 1, Vacaciones turnca (días)', required=True,
                                   default=lambda self: self.env.context.get('cut_vacations', 0))
    cut_vacations_m2 = fields.Integer(string='Periodo 2, Vacaciones turnca (meses)', required=True,
                                      default=lambda self: self.env.context.get('cut_vacations_m2', 0))
    cut_vacations_d2 = fields.Integer(string='Periodo 2, Vacaciones turnca (días)', required=True,
                                      default=lambda self: self.env.context.get('cut_vacations_d2', 0))
    afp = fields.Float(string='APF', required=True, default=lambda self: self.env.context.get('afp', 0))

    gratification_description = fields.Char(string='Gratificación',
                                            default=lambda self: self.env.context.get('gratification_description', ''))
    cut_gratification = fields.Integer(string='Meses gratificación', required=True,
                                       default=lambda self: self.env.context.get('cut_gratification', 0))
    bonus = fields.Float(string='Bonificacion Extraordinaria - 9%', required=True,
                         default=lambda self: self.env.context.get('bonus', 0))
    cts_period = fields.Integer(string='CTS - Periodo (meses)', required=True,
                                default=lambda self: self.env.context.get('cts_period', 0))

    # TODO Implementar la funcion que calcule el promedio
    def get_overtime_average(self):
        return 0.0

    def action_print(self):
        if self.cut_gratification == 0:
            raise ValidationError('El valor del campo Meses gratificación debe ser mayor que cero')

        employee = self.employee_id
        employee.liquidation_date_init = self.date_init
        employee.average_gratification = self.average_gratification
        employee.overtime_average = self.overtime_average
        employee.cut_vacations = self.cut_vacations
        employee.cut_vacations_m2 = self.cut_vacations_m2
        employee.cut_vacations_d2 = self.cut_vacations_d2
        employee.afp = self.afp
        employee.gratification_description = self.gratification_description
        employee.cut_gratification = self.cut_gratification
        employee.bonus = self.bonus
        employee.cts_period = self.cts_period

        if self.employee_id.contract_id.wage_type == 'monthly':
            wage = self.employee_id.contract_id.wage
        else:
            wage = self.employee_id.contract_id.hourly_wage * 30

        remuneration = wage + self.employee_id.contract_id.da + self.overtime_average
        vac_perio_dia = remuneration / 30
        vac_perio_total = vac_perio_dia * self.cut_vacations
        vac_periom2_total = vac_perio_dia * self.cut_vacations_m2
        vac_period2_total = vac_perio_dia * self.cut_vacations_d2
        vac_sub_total = vac_perio_total + vac_periom2_total + vac_period2_total
        employee.vacations_trunc = vac_sub_total
        cut_grat = remuneration / self.cut_gratification
        employee.gratification = cut_grat * self.cut_gratification

        return self.env.ref('cabalcon_hr_payroll.action_liquidation_report').report_action(employee)
