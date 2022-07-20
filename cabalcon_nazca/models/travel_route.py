# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['image.mixin','tms.travel']

    departure_id = fields.Many2one('tms.place', 'Salida', required=True)
    arrival_id = fields.Many2one('tms.place', 'Llegada', required=True)
    operation_ids = fields.One2many('tms.route.operation', 'travel_id', string='Trasnporte', copy=False, domain=[('type', '=', 'transporte')])
    custody_ids = fields.One2many('tms.route.operation', 'travel_id', string='Custodia', copy=False, domain=[('type', '=', 'custodia')])
    stowage_ids = fields.One2many('tms.route.operation', 'travel_id', string='Estiba', copy=False, domain=[('type', '=', 'estiba')])
    certifying_ids = fields.One2many('tms.route.operation', 'travel_id', string='Certificadora', copy=False, domain=[('type', '=', 'certificadora')])
    custom_agency = fields.Many2one('tms.custom.agency', 'Agencia de aduanas')
    ship_id = fields.Many2one('tms.ship', string='Nave')
    booking_id = fields.Many2one('tms.booking', string='Booking')
    service_ids = fields.Many2many('tms.type.service', string="Servicios")