# -*- coding: utf-8 -*-

from odoo import models, fields, api

#Tipo Track
TYPE_TRACK = [('tracking', 'Seguimiento'), ('incidence', 'Incidencia')]

class TmsStatusTrack(models.Model):
    _name = 'tms.status.track'
    _description = "Estados de Seguimiento"
    _order = 'sequence asc'

    operation_type = fields.Many2one('tms.route.operation.type', string="Tipo de Operación", required=True)
    name = fields.Char(string='Estado', required=True)
    type_tracking = fields.Selection(TYPE_TRACK, default='tracking', required=True, string='Tipo')
    sequence = fields.Integer(help="Usado para ordenar los registros", default=99)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [ ('001_name_operation', 'unique(operation_type, name)', 'El Estado ya existe!') ]
    