# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TmsShipper(models.Model):
    _name = 'tms.shipper'

    name = fields.Char("Nombre del embarcador")