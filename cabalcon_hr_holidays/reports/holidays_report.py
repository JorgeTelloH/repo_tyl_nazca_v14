# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class HolidaysReport(models.AbstractModel):
    _name = 'report.cabalcon_hr_holidays.report_leave'
    _description = 'Reporte de ausencias'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']

        domain = [('date_from', '<=', date_to),
                  ('date_to', '>=', date_from),]

        if data['form']['leave_type_id']:
           holiday_status_id = data['form']['leave_type_id'][0]
           a = ('holiday_status_id', '=', holiday_status_id)
           domain.append(a)

        if data['form']['employee_id']:
            employee_id = data['form']['employee_id'][0]
            a = ('employee_id', '=', employee_id)
            domain.append(a)

        holidays = self.env['hr.leave'].sudo().search(domain, order='date_from asc')

        return {
            'doc_ids': holidays.ids,
            'doc_model': 'hr.leave',
            'docs': holidays,

        }