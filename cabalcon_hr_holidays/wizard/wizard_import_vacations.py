# -*- coding: utf-8 -*-
import base64
from tempfile import TemporaryFile
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError
from odoo.tools import pycompat
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import datetime

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None


class WizardImportAssignmentsVacations(models.TransientModel):
    _name = "wizard.import.assignments.vacations"
    _description = "Asistente para importar asignación de vacaciones"

    binary_file = fields.Binary('Archivo',  required=True)
    file_name = fields.Char('File Name', required=True)
    name = fields.Char(string='Nombre',  required=True, default='Carga de asignación de vacaciones')
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.user.company_id)
    allow_negative = fields.Boolean(string='Permitir valores negativo', default=False)

    def import_file(self):
        file = base64.b64decode(self.binary_file)
        excel_fileobj = TemporaryFile('wb+')
        excel_fileobj.write(file)
        excel_fileobj.seek(0)

        book = xlrd.open_workbook(file_contents=file)
        sheet = book.sheet_by_index(0)

        employee = self.env['hr.employee']
        allocation = self.env['hr.leave.allocation']
        objerror = self.env['hr_import_vacations.error']

        objerror.search([]).unlink()

        def to_date(cell):
            if cell.ctype is xlrd.XL_CELL_DATE:
                dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                return dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
            else:
                raise UserError(_("Error in the date format, the cell must be formatted %s" % DEFAULT_SERVER_DATE_FORMAT))

        def to_float(cell):
            if cell.ctype is xlrd.XL_CELL_NUMBER:
                return str(cell.value)
            else:
                return 0.0

        def to_int(cell):
            if cell.ctype is xlrd.XL_CELL_NUMBER:
                return str(int(cell.value))
            elif cell.ctype is xlrd. XL_CELL_TEXT:
                return str(int(cell.value))
            else:
                return 0

        def to_str(cell):
            if cell.ctype is xlrd.XL_CELL_NUMBER:
                return str(int(cell.value))
            elif cell.ctype is xlrd. XL_CELL_TEXT:
                return cell.value
            else:
                return ''

        count_row = 0
        # for row in pycompat.imap(sheet.row, range(sheet.nrows)):
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):

            if count_row == 0:
                if row[0].value != 'DNI':
                    raise UserError("Error: Verifique que el archivo tenga el formato correcto.")
            else:
                ci = to_str(row[0])
                if ci == '':
                    break
                emp = employee.search([('identification_id', '=', ci), ('company_id', '=', self.company_id.id)], limit=1)
                if emp:
                    employee_id = emp.id
                    tiempo = to_float(row[1])
                    validity_start = to_date(row[2])
                    validity_stop = to_date(row[3])

                    # holiday_status_id buscar el id
                    holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vac')
                    name = self.name + ' para ' + emp.name
                    leave = {'name': name,
                             'employee_id': employee_id,
                             'holiday_status_id': holiday_status_id.id,
                             'holiday_type': 'employee',
                             'allocation_type': 'regular',
                             'number_of_days': tiempo,
                             'date_from': validity_start,
                             'valid_period_from': validity_start,
                             'valid_period_to': validity_stop,
                             'state': 'confirm',
                             }

                    leaveresult = allocation.sudo().search([('employee_id', '=', employee_id),
                                                 ('holiday_status_id', '=', holiday_status_id.id), ])
                    if leaveresult:
                        allocation.sudo().write(leave)
                    else:
                        allocation.sudo().create(leave)

                else:
                    objerror.create({'ci': ci, 'error': _("No encontro al empleado %s - %s" % (to_str(row[2]), to_str(row[3]) ))})
                    continue

            count_row += 1

        if len(objerror.search([])) > 0:
            return {
                'name': 'Errores detectados en la Importación',
                'type': 'ir.actions.act_window',
                'res_model': 'hr_import_vacations.error',
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': False,
                'target': 'new',
            }

