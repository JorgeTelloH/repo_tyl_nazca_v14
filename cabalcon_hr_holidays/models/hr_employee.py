# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, _, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    days_worked_of_year = fields.Float(string='Días trabajados en el año')
    number_unexcused_absences = fields.Float(string='Cantidad de ausencias injustificadas')
    days_vacation = fields.Float(string='Días de vacaciones', compute='_compute_days_vacation')
    acumulate_vacation = fields.Float(string='Vacaciones acumuladas del periodo')
    # para llevar el periodo del año de trabajo
    validity_start = fields.Datetime(string='Fecha inicio del año de trabajo')
    validity_stop = fields.Datetime(string='Fecha fin del año de trabajo')

    def leave_vacations_trunca(self, employee, validity_start):
        holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vactruncas')
        sql = """ SELECT holiday_status_id, sum(number_of_days) as number_of_days
                  FROM hr_leave
                  WHERE state='validate' AND holiday_status_id = %s AND employee_id = %s
                  and date_from >= '%s'
                  GROUP BY holiday_status_id
            """ % (holiday_status_id.id, employee.id, validity_start)
        self._cr.execute(sql)
        result = self._cr.dictfetchone()
        day = 0
        if result:
           day = result.get('number_of_days')
        return day

    def _compute_worked_days_cron(self):
        dt = datetime.now()
        for employee in self.search([]):
            if employee.validity_start and employee.validity_stop:
                if employee.first_contract_date and not employee.validity_start:
                    employee.validity_start = datetime.combine(employee.first_contract_date, datetime.min.time())
                    employee.validity_stop = employee.validity_start + relativedelta(years=1)
                else:
                    valid = ((dt < employee.validity_stop) and (dt > employee.validity_start))
                    if not valid:
                        employee.validity_start = employee.validity_stop + relativedelta(days=1)
                        employee.validity_stop = employee.validity_start + relativedelta(years=1)

                validity_start = employee.validity_start
                validity_stop = dt
                if validity_start and validity_stop:
                    days_worked_of_year = employee._get_work_days_data_batch(
                        validity_start, validity_stop,
                        domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
                    )[employee.id]['days']

                    number_unexcused_absences = employee._get_leave_days_data_batch(
                        validity_start, validity_stop,
                        domain=[('holiday_id.holiday_status_id.unpaid', '=', True), ('time_type', '=', 'leave')]
                    )[employee.id]['days']

                    acumulate_vacation = days_worked_of_year/30*2.5 - self.leave_vacations_trunca(employee, validity_start)

                    values = {'days_worked_of_year': days_worked_of_year,
                              'number_unexcused_absences': number_unexcused_absences,
                              'acumulate_vacation': acumulate_vacation}
                    employee.write(values)

    def _generate_leave_allocation_vac_cron(self):
        dt = datetime.now()
        allocation = self.env['hr.leave.allocation']
        employees = self.sudo().search([('validity_stop', '<=', dt)])
        for employee in employees:
            valid = True
            vacation_record = employee.resource_calendar_id.vacation_record
            if employee.number_unexcused_absences >= employee.company_id.number_absences:
                valid = False

            if valid:
                # holiday_status_id buscar el id
                holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vac')
                name = holiday_status_id.name + ' para ' + employee.name
                number_of_days_display = employee.company_id.vacation_days_allowed
                validity_start = employee.validity_stop + relativedelta(days=1)
                validity_stop = validity_start + relativedelta(years=1)

                values = {'name': name,
                          'employee_id': employee.id,
                          'holiday_status_id': holiday_status_id.id,
                          'holiday_type': 'employee',
                          'allocation_type': 'regular',
                          'number_of_days': number_of_days_display,
                          'date_from': validity_start,
                          'valid_period_from': validity_start,
                          'valid_period_to': validity_stop,
                          'state': 'draft',
                          }
                result = allocation.sudo().search([('employee_id', '=', employee.id),
                                                   ('holiday_status_id', '=', holiday_status_id.id),
                                                   ('date_from', '=', validity_start)])
                if not result:
                    allocation_obj = allocation.sudo().create(values)
                    if employee.days_worked_of_year >= vacation_record:
                        allocation_obj.action_confirm()
                        allocation_obj.action_approve()

    def remaining_leave_vacations(self, employee):
        holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vac')
        sql = """SELECT sum(h.number_of_days) AS days, h.employee_id
                 FROM
                     (
                        SELECT holiday_status_id, number_of_days, state, employee_id
                        FROM hr_leave_allocation
                        UNION ALL
                        SELECT holiday_status_id, (number_of_days * -1) as number_of_days, state, employee_id
                        FROM hr_leave
                     ) h
                     join hr_leave_type s ON (s.id=h.holiday_status_id)
                 WHERE
                     s.active = true AND h.state='validate' AND
                     (s.allocation_type='fixed' OR s.allocation_type='fixed_allocation') AND holiday_status_id = %s 
                     AND h.employee_id = %s
                 GROUP BY h.employee_id
            """ % (holiday_status_id.id, employee.id)
        self._cr.execute(sql)
        result = self._cr.dictfetchone()
        day = 0
        if result:
           day = result.get('days')
        return day

    def _notification_leave_allocation_vac_cron(self):
        dt = datetime.now() + relativedelta(days=45)
        for employee in self.search([('validity_stop', '<', dt)]):
            days = self.remaining_leave_vacations(employee)
            if days > 0:
                template = self.env.ref('cabalcon_hr_holidays.email_template_notification_vacations')
                if employee.work_email:
                    template.write({'email_to': employee.work_email})
                    template.send_mail(employee.id, force_send=True)

                users = employee.company_id.notification_vac_expiration_ids
                template = self.env.ref('cabalcon_hr_holidays.email_template_notification_vacations_officer')
                for user in users:
                    if user.work_email:
                        template.write({'email_to': user.work_email})
                        template.send_mail(employee.id, force_send=True)

    def _compute_days_vacation(self):
        for employee in self:
            employee.days_vacation = self.remaining_leave_vacations(employee)

