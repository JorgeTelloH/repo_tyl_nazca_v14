# -*- coding: utf-8 -*-
import io
import os
import base64
import zipfile
from lxml import etree
from datetime import timedelta, datetime
from jinja2 import FileSystemLoader, Environment
from odoo import osv, models, fields, api, _, SUPERUSER_ID


class StockPicking(models.Model):
    _inherit = "stock.picking"

    catalog_20 = fields.Many2one(comodel_name='catalogs.sunat.guia',  string='Motivo de traslado')
    type_modality = fields.Selection(string='Modalidad', 
        selection=[('02', 'Privado'),
                   ('01', 'Publico')
                   ], default='02')

    transport_uom_id = fields.Many2one('uom.uom', string='Unidad medida traslado', ondelete='set null', index=True, oldname='uos_id')
    transport_quantity = fields.Float(string='Cantidad traslado')
    is_guie = fields.Boolean(string='Es guia')
    serie = fields.Char(string='Serie', 
        #readonly=True
    )
    numero = fields.Char(string='Numero',
        # readonly=True
    )
    direccion_salida = fields.Char(string='Direccion salida',
        #readonly=True
    )
    direccion_llegada = fields.Char(string='Direccion llegada',
        #readonly=True
    )
    partner_transport_id = fields.Many2one('res.partner', string='vehiculos y personas')
    trasnportista = fields.One2many('picking.vehiculo', 'picking_id', string='Trasnportista')

    @api.onchange("is_guie")
    def _onchange_is_guie(self):
        if self.is_guie:
            self.direccion_salida = self.company_id.street
            self.direccion_llegada = self.partner_id.street


class PickingVehiculo(models.Model):
    _name = 'picking.vehiculo'

    vehicle_brand = fields.Char(string='Marca del vehiculo', required=True)
    vehicle_model = fields.Char(string='Modelo del vehiculo', required=True)
    license_plate = fields.Char(string='Número de placa')
    partner_id = fields.Many2one('res.partner', string='vehiculos y personas')
    picking_id = fields.Many2one('stock.picking', string='Transferencia')

