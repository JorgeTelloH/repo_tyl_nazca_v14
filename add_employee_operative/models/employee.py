# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    operative_to_customer = fields.Boolean(string='Operativo asignado a Cliente?', help='Activar si el Operativo debe ser asignado al Cliente')
    is_dispatcher = fields.Boolean(string='Es un Despachador?', help='Activar si es un Despachador asignado al Flete')
