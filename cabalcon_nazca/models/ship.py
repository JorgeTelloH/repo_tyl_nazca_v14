# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Ship(models.Model):
    _name = 'tms.ship'
    _inherit = 'image.mixin'

    imo = fields.Char("IMO")
    name = fields.Char("Nombre de la embarcacion")
    state = fields.Selection([
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo')
    ], 'estado de la embarcacion', default='activo', help='estado de la embarcacion', required=True)

    image_128 = fields.Image("Image 128", compute='_compute_image', compute_sudo=True)
    flag = fields.Many2one('res.country', 'Bandera', required=True)
    type_generic = fields.Many2one('type.generic', 'Tipo generico de embarcacion', required=True)
    type_generic2 = fields.Many2one('type.generic2', 'Tipo generico de embarcacion', required=True)
    mmsi = fields.Char("Codigo MMSI")
    signal = fields.Char("Señal de llamado")

    gross_tonnage = fields.Char("Tonelaje bruto")
    dead_tonnage = fields.Char("Tonelaje muerto")
    length = fields.Char("Longitud")
    port_id = fields.Many2one('tms.port', string='Puerto')

    departure = fields.Char("Partida")
    date_etd_from = fields.Datetime('ETD', help='Estimate time of departure ')
    date_atd_from = fields.Datetime('ATD', help='Actual time of departure ')
    arrival = fields.Char("Llegada")
    date_etd_from_arrival = fields.Datetime('ETD', help='Estimate time of arrival ')
    date_atd_from_arrival = fields.Datetime('ETD', help='Actual time of arrival ')

    positon_receved = fields.Char("Posicion")
    vessel_local_time = fields.Char("Hora local del barco")
    area = fields.Char("Area")
    lat_log = fields.Char("Latitude/longitude")
    status_pos = fields.Selection([
        ('moored', 'Amarrada'),

    ], 'Estatus', default='moored', help='estatus')
    sped_cursed = fields.Char("Estado/Curso")
    ais_source = fields.Char("Fuente")

    booking_ids = fields.One2many('tms.booking', 'ship_id', string='Booking', copy=False)

    # booking_ids = fields.One2many(
    #     "invoice.payment.line", "wizard_id", string="Payments"
    # )






