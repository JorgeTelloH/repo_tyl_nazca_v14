# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    notification_request_job_ids = fields.Many2many('hr.employee', 'request_job_rel', 'company_id', 'employee_id', string='Notificar solicitud de nuevos puestos')
