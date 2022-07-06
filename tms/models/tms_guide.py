# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TmsGuide(models.Model):
    _name = 'tms.guide'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Guias del viaje'
    _order = "guide_date"

    name = fields.Char(string= 'Nro Guia', required=True, index=True)
    travel_id = fields.Many2one('tms.travel', string='Viaje', required=True)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    sequence = fields.Integer(string='secuencia', default=99)
    guide_date = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    notes = fields.Text(string='Observaciones')