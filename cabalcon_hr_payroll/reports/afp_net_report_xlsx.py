# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields
from odoo.exceptions import UserError, ValidationError


class ReconciliationReportXlsx(models.AbstractModel):
    _name = "report.cabalcon_hr_payroll.afp_net_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte AFP Net"

    def labor_relation_started(seft, ddate, _date):
        if _date.year == ddate.year and _date.month == ddate.month:
            return 'S'
        else:
            return 'N'

    def labor_relation_finished(self, ddate, _date):
        if ddate and _date.year == ddate.year and _date.month == ddate.month:
            return 'S'
        else:
            return 'N'

    def remuneracin_asegurable(self, contract_id, date_from, date_to, confirm):
        # aqui deberia buscar todo lo que alla devengado
        domain = [
            ('contract_id', '=', contract_id.id),
            ('credit_note', '=', False),
            ('refund', '=', False),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ]
        if confirm:
            domain += [('state', '=', 'done')]
        else:
            domain += [('state', '!=', 'cancel')]
        payslip = self.env['hr.payslip'].search(domain, limit=1)._get_salary_line_total('TOTALIMP')
        return payslip

    def exception_make_contribution(self, employee_id, date_from, date_to, confirm):
        holiday_status_ids = self.env['hr.leave.type'].search([('code_afpnet', 'in', ['L', 'U', 'I', 'J'])]).ids

        leaves = self.env['hr.leave'].search([
            ('employee_id', '=', employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_type', '=', 'employee'),
            ('holiday_status_id', 'in', holiday_status_ids),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
        ])
        result = ''
        if not leaves:
            domain = [
                ('contract_id', '=',employee_id.contract_id.id),
                ('credit_note', '=', False),
                ('refund', '=', False),
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to),
            ]
            if confirm:
                domain += [('state', '=', 'done')]
            else:
                domain += [('state', '!=', 'cancel')]
            payslip = self.env['hr.payslip'].search(domain, limit=1)
            if not payslip:
                if employee_id.contract_id.date_start > date_from:
                    result = 'P'
                else:
                    result = 'O'
        else:
            result = leaves.holiday_status_id.code_afpnet

        return result

    def generate_xlsx_report(self, workbook, data, employees):

        employees = self.env['hr.employee'].browse(data['data_report'])
        date_from = data['date_from']
        date_to = data['date_to']
        confirm = data['confirm']
        _date = fields.Date.to_date(date_from)

        bold = workbook.add_format({"bold": True, 'valign': 'vcenter', 'text_wrap': True, "align": "center"})
        sheet = workbook.add_worksheet('Plantilla')

        show_header = data['show_header']
        headers = ['Número de secuencia', 'CUSPP', 'Tipo de documento de identidad', 'Número de documento de indentidad',
                   'Apellido paterno', 'Apellido materno', 'Nombres', 'Relación Laboral', 'Inicio de RL', 'Cese de RL',
                   'Excepcion de Aportar', 'Remuneración asegurable', 'Aporte voluntario del afiliado con fin previsional',
                   'Aporte voluntario del afiliado sin fin previsional', 'Aporte voluntario del empleador',
                   'Tipo de trabajo o Rubro', 'AFP (Conviene dejar en blanco)']

        row = 0
        if show_header:
            col = 0
            for header in headers:
                sheet.write(row, col, header, bold)
                col += 1
            row = 1

        sheet.set_column(0, 1, 8)
        sheet.set_column(0, 2, 8)
        sheet.set_column(0, 3, 15)
        sheet.set_column(0, 4, 10)
        sheet.set_column(0, 5, 10)
        sheet.set_column(0, 6, 8)
        sheet.set_column(0, 7, 8)
        sheet.set_column(0, 8, 8)
        sheet.set_column(0, 9, 8)
        sheet.set_column(0, 10, 10)
        sheet.set_column(0, 11, 10)
        sheet.set_column(0, 12, 12)
        sheet.set_column(0, 13, 12)
        sheet.set_column(0, 14, 12)
        sheet.set_column(0, 15, 12)
        sheet.set_column(0, 16, 15)

        item = 1
        for emp in employees:
            if emp.contract_id:
                sheet.write(row, 0, item)
                sheet.write(row, 1, emp.CUSPP or '')
                sheet.write(row, 2, int(emp.document_type.cod_afp_net) or 0)
                sheet.write(row, 3, emp.identification_id or '')
                sheet.write(row, 4, emp.lastname)
                sheet.write(row, 5, emp.lastname2 or '')
                sheet.write(row, 6, emp.firstname)
                sheet.write(row, 7, 'S' if emp.contract_id.state == 'open' else 'N')
                sheet.write(row, 8, self.labor_relation_started(emp.contract_id.date_start, _date))
                sheet.write(row, 9, self.labor_relation_finished(emp.contract_id.date_end, _date))
                sheet.write(row, 10, self.exception_make_contribution(emp, _date, date_to, confirm))
                sheet.write(row, 11, self.remuneracin_asegurable(emp.contract_id, _date, date_to, confirm) or '')
                sheet.write(row, 12, emp.contract_id.voluntary_contribution if emp.contract_id.is_voluntary_contribution else 0)
                sheet.write(row, 13, emp.contract_id.voluntary_endless_contribution if emp.contract_id.is_voluntary_endless_contribution else 0)
                sheet.write(row, 14, '')
                sheet.write(row, 15, emp.type_work or '')
                sheet.write(row, 16, emp.afp_id.code or '')
                item += 1
                row += 1





