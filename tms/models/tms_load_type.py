# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TmsEventType(models.Model):
    _name = 'tms.load.type'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Tipo de Mercaderia'
    _order = "name"

    name = fields.Char(string='Tipo de Mercadería', required=True)
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [ ('001_name', 'unique(name)', 'Tipo de Mercadería ya existe!') ]

