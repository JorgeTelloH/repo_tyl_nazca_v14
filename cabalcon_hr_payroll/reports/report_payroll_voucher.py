# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class PayrollVoucherReport(models.AbstractModel):
    _name = 'report.hr_payroll.report_payslip_lang'
    _description = 'Boleta de pago'

    def get_basic(self, payslip_id):
        return self.env['hr.payslip.line'].search([('slip_id', '=', payslip_id), ('code', '=', 'BASIC')], limit=1)

    def get_remunerations(self, payslip_id):
        cat_ids = [self.env.ref('hr_payroll.ALW').id]
        lines = self.env['hr.payslip.line'].search([('slip_id', '=', payslip_id), ('appears_on_payslip', '=', 'True'),
                                                    ('category_id', 'in', cat_ids),
                                                    ('is_employer_contributions', '=', False)])
        return lines

    def get_deductions(self, payslip_id):
        cat_ids = [self.env.ref('hr_payroll.DED').id]
        lines = self.env['hr.payslip.line'].search([('slip_id', '=', payslip_id), ('appears_on_payslip', '=', 'True'),
                                                    ('category_id', 'in', cat_ids)])
        return lines

    def get_employer_contributions(self, payslip_id):
        cat_ids = [self.env.ref('hr_payroll.COMP').id]
        lines = self.env['hr.payslip.line'].search([('slip_id', '=', payslip_id), ('appears_on_payslip', '=', 'True'),
                                                    ('category_id', 'in', cat_ids),
                                                    ('is_employer_contributions', '=', True)])
        return lines

    def get_date_to_report(self, date):
        months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
                  "Noviembre", "Diciembre")
        _date = ''
        if date:
            month = months[date.month - 1]
            _date = "MES DE {}  {}".format(month, date.year)

        return _date

    # obtener la imformacion de las vacaciones
    def get_vacations(self, employee_id, date_from, date_to):
        holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vac')
        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', '=', employee_id.id),
            ('holiday_status_id', '=', holiday_status_id.id),
            ('state', 'in', ['confirm', 'validate']),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
        ], limit=1)
        values = {'date_from': False, 'date_to': False, 'days': 0}
        if holidays:
            values['date_from'] = holidays.date_from.date()
            values['date_to'] = holidays.date_to.date()
            values['days'] = holidays.number_of_days
        return values

    def get_hours_extra(self, employee_id, date_from, date_to):
        overtimes = self.env['calendar.operation'].search([('employee_id', '=', employee_id.id),
                                                       ('date', '>=', date_from),
                                                       ('date', '<=', date_to),
                                                       ('approve', '=', True)])
        # hours_extra_25 = 0
        # hours_extra_35 = 0
        hours_extra = 0

        for ovt in overtimes:
            # hours_extra_25 += ovt.hours_extra_25
            # hours_extra_35 += ovt.hours_extra_35
            hours_extra += ovt.hours_extra

        return hours_extra

    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'data': data,
            'get_remunerations': self.get_remunerations,
            'get_deductions': self.get_deductions,
            'get_employer_contributions': self.get_employer_contributions,
            'get_date_to_report': self.get_date_to_report,
            'get_basic': self.get_basic,
            'get_hours_extra': self.get_hours_extra,
            'get_vacations': self.get_vacations,
        }
