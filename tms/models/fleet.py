# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    vehicle_capacity_id = fields.Many2one('fleet.vehicle.capacity', string='Capacidad del vehículo')
    platform_gps_id = fields.Many2one('res.partner.platform.gps', string="Plataforma GPS")