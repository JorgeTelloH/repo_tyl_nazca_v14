# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields
from odoo.exceptions import UserError, ValidationError


class ReconciliationWeekReportXlsx(models.AbstractModel):
    _name = "report.cabalcon_hr_payroll.afp_net_week_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte AFP Net Semanal"

    # def labor_relation_started(seft, ddate, _date):
    #     if _date.year == ddate.year and _date.month == ddate.month:
    #         return 'S'
    #     else:
    #         return 'N'
    #
    # def labor_relation_finished(self, ddate, _date):
    #     if ddate and _date.year == ddate.year and _date.month == ddate.month:
    #         return 'S'
    #     else:
    #         return 'N'
    #
    # def remuneracin_asegurable(self, contract_id, date_from, date_to):
    #     # aqui deberia buscar todo lo que alla devengado
    #     payslip = self.env['hr.payslip'].search([
    #         ('contract_id', '=', contract_id.id),
    #         ('state', '=', 'done'),
    #         ('date_from', '>=', date_from),
    #         ('date_to', '<=', date_to),
    #     ], limit=1).net_wage
    #     return payslip
    #
    # def exception_make_contribution(self, employee_id, date_from, date_to):
    #     holiday_status_ids = self.env['hr.leave.type'].search([('code_afpnet', 'in', ['L', 'U', 'I', 'J'])]).ids
    #
    #     leaves = self.env['hr.leave'].search([
    #         ('employee_id', '=', employee_id.id),
    #         ('state', '=', 'validate'),
    #         ('holiday_type', '=', 'employee'),
    #         ('holiday_status_id', 'in', holiday_status_ids)
    #         ('date_from', '>=', date_from),
    #         ('date_to', '<=', date_to),
    #     ])
    #     result = ''
    #     if not leaves:
    #         payslip = self.env['hr.payslip'].search([
    #             ('contract_id', '=', employee_id.contract_id.id),
    #             ('state', '=', 'done'),
    #             ('date_from', '>=', date_from),
    #             ('date_to', '<=', date_to),
    #         ], limit=1)
    #         if not payslip:
    #             result = 'P'
    #     else:
    #         result = leaves.holiday_status_id.code_afpnet
    #
    #     return result

    def generate_xlsx_report(self, workbook, data, employees):

        employees = self.env['hr.employee'].browse(data['data_report'])
        date_from = data['date_from']
        date_to = data['date_to']
        _date = fields.Date.to_date(date_from)
        week = data['week']

        bold = workbook.add_format({"bold": True, 'valign': 'vcenter', 'text_wrap': True, "align": "center"})
        sheet = workbook.add_worksheet('Plantilla')

        show_header = data['show_header']
        headers = ['No.','Tipo de documento de identidad', 'Número de documento de indentidad',
                   'Número de semana contributiva', 'Indicador de producción pesquera', 'Código de cargo desempeñado en la semana', ]

        row = 0
        if show_header:
            col = 0
            for header in headers:
                sheet.write(row, col, header, bold)
                col += 1
            row = 1

        sheet.set_column(0, 1, 4)
        sheet.set_column(0, 2, 25)
        sheet.set_column(0, 3, 25)
        sheet.set_column(0, 4, 25)
        sheet.set_column(0, 5, 25)
        sheet.set_column(0, 6, 25)

        item = 1
        for emp in employees:
            if emp.contract_id:
                sheet.write(row, 0, item)
                sheet.write(row, 1, int(emp.document_type.cod_afp_net) or 0)
                sheet.write(row, 2, emp.identification_id or '')
                sheet.write(row, 3, week)
                sheet.write(row, 4, '')
                sheet.write(row, 5, '')

                item += 1
                row += 1





