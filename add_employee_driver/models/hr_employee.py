# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime

class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    driver = fields.Boolean(string='Es Conductor?', help='Usado para definir si esta persona es un conductor')
    type_employee = fields.Selection([("planilla", "Planilla"), ("tercero", "Tercero")], string='Tipo de empleado', defautl='planilla')
    partner_id = fields.Many2one('res.partner', string='Proveedor', index=True)
    driver_license = fields.Char(string='Nro Licencia')
    license_type = fields.Char(string='Tipo de Licencia')
    license_expiration = fields.Date(string='Fecha de caducidad')
    days_to_expire = fields.Integer(compute='_compute_days_to_expire', string='Días de caducidad')
    require_license = fields.Boolean(string='Requiere licencia')

    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        for rec in self:
            now = datetime.now()
            date_expire = rec.license_expiration or  datetime.now()
            delta = date_expire - now
            if delta.days >= -1:
                rec.days_to_expire = delta.days + 1
            else:
                rec.days_to_expire = 0
