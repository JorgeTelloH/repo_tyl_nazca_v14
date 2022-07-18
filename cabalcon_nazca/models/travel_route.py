# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TmsTravel(models.Model):
    _inherit = 'tms.travel'

    departure_id = fields.Many2one('tms.place', 'Salida', required=True)

    arrival_id = fields.Many2one('tms.place', 'Llegada', required=True)

    operation_ids = fields.One2many('tms.route.operation', 'travel_id', string='Operaciones', copy=False)