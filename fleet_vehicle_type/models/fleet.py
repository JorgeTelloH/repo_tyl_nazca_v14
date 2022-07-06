# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    vehicle_type_id = fields.Many2one('fleet.vehicle.type', string='Tipo de vehiculo')