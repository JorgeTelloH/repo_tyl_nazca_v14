# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LineTmsShipper(models.Model):
    _name = 'tms.line.shipper'

    name = fields.Char("Nombre dela linea embarcador")