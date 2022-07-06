# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TmsAlarmEmail(models.Model):
    _name = 'tms.alarm.email'
    _description = 'Email de Alarmas'

    name = fields.Char('Nombre del Destinatario', size=20, required=True, index=True)
    email_to = fields.Char(string='Email del Destinatario', required=True)
    notes = fields.Text(string='Notas')
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    active = fields.Boolean(string="Activo", default=True)
    tracking_alarm = fields.Boolean(string="Seguimiento Operaciones", default=False, 
        help='Activar para enviar Email de Seguimiento de Operaciones en Rojo')

    _sql_constraints = [ ('001_email_to', 'unique(email_to)', 'El Email del Destinatario ya existe!') ]
