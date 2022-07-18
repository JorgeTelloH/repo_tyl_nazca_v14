import logging

from odoo import models, fields, api

class Operation(models.Model):
    _inherit = 'tms.route.operation'

    # licence_plate = fields.Char(string='Placa', related='vehicle_id.licence_plate',
    #                                    store=True, )

    driver_code = fields.Char(string='Codigo de conductor', related='driver_id.pin',
                                store=True, )

