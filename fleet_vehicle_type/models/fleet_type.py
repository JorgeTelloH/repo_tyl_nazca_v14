# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicleType(models.Model):
    _name = "fleet.vehicle.type"
    _description = "Tipo de vehiculo de Flota"
    _order = 'name asc'

    name = fields.Char(string='Tipo', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [ ('001_name', 'unique(name)', 'Tipo de vehículo ya existe !') ]