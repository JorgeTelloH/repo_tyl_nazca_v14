# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TypeService(models.Model):
    _name = 'tms.type.service'

    name = fields.Char("Nombre")