# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Fabricante', required=True,
                               help='Manufacturer of the vehicle')

    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Fabricante', required=True,
                               help='Manufacturer of the vehicle')