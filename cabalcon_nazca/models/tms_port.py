# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TmsPort(models.Model):
    _name = 'tms.port'

    name = fields.Char("Nombre del puerto")
    pais = fields.Many2one('res.country', 'Bandera', required=True)