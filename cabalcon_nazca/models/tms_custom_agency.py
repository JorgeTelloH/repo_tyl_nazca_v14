# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Customagency(models.Model):
    _name = 'tms.custom.agency'

    name = fields.Char("nombre de agencia")