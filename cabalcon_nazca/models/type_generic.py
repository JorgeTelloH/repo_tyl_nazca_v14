# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TypeGeneric(models.Model):
    _name = 'type.generic'

    name = fields.Char("Tipo generico")

class TypeGeneric2(models.Model):
    _name = 'type.generic2'

    name = fields.Char("Tipo generico2")