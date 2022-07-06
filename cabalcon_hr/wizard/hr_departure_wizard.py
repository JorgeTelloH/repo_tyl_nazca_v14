# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    opinion = fields.Text(string="Opinión", help="Opinión que se plasmara en el Certificado de trabajo")

    def action_register_departure(self):
        employee = self.employee_id
        employee.opinion = self.opinion
        super(HrDepartureWizard, self).action_register_departure()
