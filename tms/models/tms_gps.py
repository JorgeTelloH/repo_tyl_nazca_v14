# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TmsGps(models.Model):
    _name = 'tms.gps'
    _description = 'Equipos GPS'

    name = fields.Char('GPS', size=20, required=True, index=True)
    description = fields.Char(string='Descripción')
    platform_gps = fields.Char(string= 'Plataforma GPS', index=True)
    user_name = fields.Char(string= 'Usuario')
    password = fields.Char(string= 'Password')
    platform_date = fields.Date(string="Fecha Registro", required=True, default=fields.Date.context_today)
    active = fields.Boolean(string="Activo", default=True)
    notes = fields.Text(string='Notas')
    in_loan = fields.Boolean(string="En Préstamo", default=False, help='Se activa automáticamente al realizar el préstamo o devolución del GPS.')

    _sql_constraints = [ ('001_name', 'unique(name)', 'Equipo GPS ya existe!') ]
