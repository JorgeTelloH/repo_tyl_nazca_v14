# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_operative = fields.Many2one('hr.employee', 'Personal Operativo', help='Asignar personal operativo al Cliente')
