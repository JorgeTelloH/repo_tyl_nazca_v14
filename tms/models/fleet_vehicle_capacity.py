# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicleCapacity(models.Model):
    _name = 'fleet.vehicle.capacity'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Capacidad del vehículo'
    _order = "name"

    name = fields.Char(string='Capacidad del vehículo', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [ ('001_name', 'unique(name)', 'La Capacidad ya existe!') ]

