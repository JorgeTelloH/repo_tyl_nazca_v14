# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerPlatformGps(models.Model):
    _name = 'res.partner.platform.gps'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Plataforma GPS de Partner'

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    name = fields.Char(string= 'Plataforma GPS', required=True, index=True)
    user_name = fields.Char(string= 'Usuario')
    password = fields.Char(string= 'password')
    platform_date = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    notes = fields.Text(string='Observaciones')