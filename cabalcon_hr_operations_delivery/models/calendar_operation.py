# -*- coding: utf-8 -*-
import pytz
import datetime
from datetime import timedelta
from odoo import models, fields, api, _


class CalandarDriver(models.Model):
    _inherit = 'calendar.operation'

    hours_extra_25 = fields.Float(string='Horas extras 25%', readonly=True, store=True, digits=(12, 2))
    hours_extra_35 = fields.Float(string='Horas extras 35%', readonly=True, store=True, digits=(12, 2))
    approve = fields.Boolean(string='Aprobar H.E', default=False)

    def update_data(self):
        attendance_obj = self.env['hr.attendance']
        opration_line_obj = self.env['operations.schedule.line']
        for element in self:
            calculate_hours = 0
            hours_work = 0
            hours_lunch = 0
            hours_unavailable = 0
            hours_extra = 0
            hours_extra_25 = 0
            hours_extra_35 = 0
            operatioon_lines = opration_line_obj.search(
                [('employee_id', '=', element.employee_id.id), ('date', '=', element.date)])
            if operatioon_lines:
                for operation in operatioon_lines:
                    calculate_hours = (operation.hour_to - operation.hour_from) + calculate_hours
            else:
                calculate_hours = self.employee_id.contract_id.resource_calendar_id.hours_per_day

            date = element.date
            date_time_from = datetime.datetime(date.year, date.month, date.day)

            date_time_to = (date_time_from + timedelta(days=1)) - timedelta(seconds=1)
            tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            date_time_to_tz = tz.localize(date_time_to).astimezone(pytz.utc)

            attendances = attendance_obj.search(
                [('check_in', '>=', date_time_from), ('check_out', '<=', date_time_to_tz),
                 ('employee_id', '=', element.employee_id.id)])
            for attendance in attendances:
                if attendance.attendance_type_id in ['1', '4']:
                    hours_work += attendance.worked_hours
                if attendance.attendance_type_id == '2':
                    hours_lunch += attendance.worked_hours
                if attendance.attendance_type_id == '3':
                    hours_unavailable += attendance.worked_hours
            if hours_work > calculate_hours:
                hours_extra = hours_work - calculate_hours
                if hours_extra >= 2:
                    hours_extra_25 = 2
                    hours_extra_35 = hours_extra - 2
                else:
                    hours_extra_25 = hours_extra

            element.write({'hours_work': round(hours_work, 2),
                           'hours_lunch': round(hours_lunch, 2),
                           'hours_unavailable': round(hours_unavailable, 2),
                           'description_absence': 'Asistido',
                           'hours_extra': round(hours_extra, 2),
                           'hours_extra_25': round(hours_extra_25, 2),
                           'hours_extra_35': round(hours_extra_35, 2)
                           })
        return

