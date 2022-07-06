# -*- coding: utf-8 -*-

from odoo import models, fields, api
import time


class WizardHolidaysReport(models.TransientModel):
    _name = 'wizard.holiday.report'

    date_from = fields.Date(string='Desde', required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Hasta', required=True, default=fields.Date.context_today)
    leave_type_id = fields.Many2one('hr.leave.type', string='Tipo de incidencia')
    employee_id = fields.Many2one('hr.employee', string="Employee", help='Select corresponding Employee')
    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                 default=lambda self: self.env.user.company_id)



    def print_report(self):
        self.ensure_one()
        [data] = self.read()

        datas = {
            'form': data,
        }
        return self.env.ref('cabalcon_hr_holidays.action_leave_report').report_action(self, data=datas)
