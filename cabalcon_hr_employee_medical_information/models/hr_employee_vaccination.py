
import datetime
from odoo import api, fields, models


class HrMedicalImmunizations(models.Model):
    _name = 'hr.medical.immunizations'
    _description = 'Listado de vacunas'

    name = fields.Char('Nombre', required=True)
    description = fields.Text('Descripción')
    doce_ids = fields.One2many('hr.medical.immunizations.doce', 'immunization_id', string='Dosis', required=False)
    doce_count = fields.Integer(compute="_compute_doce_count", string='Cantidad de dosis')

    @api.depends("doce_ids")
    def _compute_doce_count(self):
        for record in self:
            record.doce_count = len(record.doce_ids)


class HrMedicalImmunizationsDoce(models.Model):
    _name = 'hr.medical.immunizations.doce'
    _description = 'Listado de dosis'

    immunization_id = fields.Many2one('hr.medical.immunizations', string='Vacuna', required=True)
    name = fields.Char('Nombre', required=True)


class HrEmployeeVaccination(models.Model):
    _name = "hr.employee.vaccination"
    _description = "Información sobre la vacunación del empleado"
    _order = 'vaccine_date'
    _rec_name = 'vaccine_id'

    employee_id = fields.Many2one('hr.employee', 'Empleado', required=True)
    vaccine_id = fields.Many2one('hr.medical.immunizations', string='Vacuna', required=True)
    vaccine_date = fields.Date(string='Fecha')
    doce = fields.Many2one('hr.medical.immunizations.doce', string='Dosis', domain="[('immunization_id', '=', vaccine_id)]")
