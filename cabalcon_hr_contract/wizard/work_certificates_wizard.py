# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrWorkCertificatesWizard(models.TransientModel):
    _name = 'hr.work.certificate.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.context.get('active_id', None),
                                  )
    opinion = fields.Text(string="Opinión", help="Opinión que se plasmara en el Certificado de trabajo",
                          default=lambda self: self.env.context.get('opinion', None))

    def action_register(self):
        employee = self.employee_id
        employee.opinion = self.opinion
        return self.env.ref('cabalcon_hr_contract.action_work_certificates').report_action(employee)

