# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    alert_contract = fields.Integer(string='Alerta de vencimiento de contrato (días)', default=30)
    notification_contract_expiration_ids = fields.Many2many('hr.employee', string='Notificar contratos próximos a expirar')
    notification_vac_expiration_ids = fields.Many2many('hr.employee', 'rel_notification_vac_expiration', string='Notificar vacaciones por disfrutar')

    is_af = fields.Boolean(string='Tiene en cuenta la Asignación Familiar', default=True)
    percent_af = fields.Float(string='Porciento a tener en cuenta para AF', default=10)

    number_absences = fields.Integer(string='Cantidad de ausencias injustificadas permitidas ', default=10)
    vacation_days_allowed = fields.Integer(string='Días permitidos de vacaciones ', default=30)

    days_medical_certificate = fields.Integer(string='Días de descanso médico', default=20, help='Cantidad de días de descanso médico cubirto por la compañía')

    porcet_gratification = fields.Float(string='Porciento de gratificación', default=100)
