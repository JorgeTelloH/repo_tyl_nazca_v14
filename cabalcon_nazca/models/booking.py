import logging

from odoo import models, fields, api

class Address(models.Model):
    _name = 'tms.booking'
    _inherit = 'image.mixin'

    name = fields.Char(
        'Booking', required=True)
    partner_id = fields.Many2one('res.partner',
           string='Cliente')
    line_shipper_id = fields.Many2one('tms.line.shipper',
                                 string='Linea naviera')

    travel = fields.Char(
        'Viaje')
    booking_eta = fields.Char(
        'Booking ETA')
    booking_etd = fields.Char(
        'Booking ETD')
    port_orig_id = fields.Many2one('tms.port', string='Puerto origen')
    port_dest_id = fields.Many2one('tms.port', string='Puerto destino')
    booking_etd = fields.Char(
        'Booking ETD')
    commodity = fields.Char(
        'Mercaderia')
    type_charge = fields.Char(
        'Tipo de carga')
    quantity_container = fields.Float(
        'Cantidad de contenedores')
    type_container = fields.Many2one('tms.type.container', string='Tipo de contenedor')
    quantity_tons = fields.Float(
        'Cantidad de Tons.')
    ship_id = fields.Many2one('tms.ship', string='Nave')




