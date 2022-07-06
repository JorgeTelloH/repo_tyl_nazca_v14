
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    vaccination_ids = fields.One2many("hr.employee.vaccination", "employee_id")

    vaccination_count = fields.Integer(compute="_compute_vaccination_count")

    alert_vaccination = fields.Boolean(string='Alerta', compute="_compute_alert_vaccination")

    blood_name = fields.Selection([("A", "A"), ("B", "B"), ("O", "O"), ("AB", "AB")], "Tipo de sangre")

    blood_type = fields.Selection([("+", "+"), ("-", "-")], "Factor")

    @api.depends("vaccination_ids")
    def _compute_vaccination_count(self):
        for record in self:
            record.vaccination_count = len(record.vaccination_ids)

    def _compute_alert_vaccination(self):
        for record in self:
            if record.age and record.age >= 45:
                record.alert_vaccination = record.vaccination_count < record.vaccination_ids.vaccine_id.doce_count
            else:
                record.alert_vaccination = False


