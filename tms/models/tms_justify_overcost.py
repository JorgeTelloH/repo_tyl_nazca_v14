# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TmsJustifyOvercost(models.Model):
    _name = 'tms.justify.overcost'
    _description = "Justificación de Sobrecosto Operacional"
    _order = 'sequence asc'

    name = fields.Char(string='Justificación', required=True)
    sequence = fields.Integer(help="Usado para ordenar los registros", default=99)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [ ('001_name', 'unique(name)', 'La Justificación ya existe!') ]
