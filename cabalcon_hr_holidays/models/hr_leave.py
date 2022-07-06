# -*- coding: utf-8 -*-

import logging
from datetime import datetime, date, timedelta, time
from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    code_afpnet = fields.Selection(string='Excepción de aportar',
                                   selection=[('L', 'Licencia sin remuneración en el mes'),
                                              ('U', 'Subsidio pagado directamente por ESSALUD'),
                                              ('J', 'Pensionado por Jubilación en el mes'),
                                              ('I', 'Pensionado por Invalidez en el mes')],
                                   )


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    report_date = fields.Date(string='Fecha de reporte')
    days_insurance = fields.Integer(string='Days insurance', compute='_compute_days_insurance')
    is_vacation = fields.Boolean(string='Es una petición de vacaciones', compute='_compute_is_vacation')
    is_sick_leave = fields.Boolean(string='Es una petición por enfermedad', compute='_compute_is_vacation')

    @api.onchange('holiday_status_id')
    def onchange_holiday_status_id(self):
        holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vactruncas')
        if self.holiday_status_id and self.holiday_status_id == holiday_status_id:
            if self.employee_id.days_vacation > 0:
                self.holiday_status_id = False
                raise ValidationError(
                    "No puede sacar estas vacaciones mientras tengas vacaciones acumuladas de un periodo anterior.")
            if self.employee_id.acumulate_vacation == 0:
                self.holiday_status_id = False
                raise ValidationError(
                    "El empleado no tiene vacaciones acumulada en el periodo.")

    @api.depends('holiday_status_id')
    def _compute_is_vacation(self):
        for leave in self:
            leave.is_vacation = (leave.holiday_status_id == self.env.ref('cabalcon_hr_holidays.holiday_status_vac'))
            leave.is_sick_leave = (leave.holiday_status_id == self.env.ref('hr_holidays.holiday_status_sl'))

    @api.depends('number_of_days')
    def _compute_days_insurance(self):
        for leave in self:
            leave.days_insurance = 0
            dmc = leave.employee_id.company_id.days_medical_certificate
            if leave.is_sick_leave and leave.number_of_days > dmc:
                leave.days_insurance = leave.number_of_days - dmc
