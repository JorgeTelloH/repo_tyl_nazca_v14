# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerAlerts(models.Model):
    _name = 'res.partner.alerts'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Alertas de Partner'

    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='cascade', index=True)
    name = fields.Char(string='Código', required=True, size=4)
    message = fields.Text(string= 'Mensaje', required=True)
    alert_active = fields.Selection([('activo','Activo'),('inactivo','Inactivo')], string='Activo', default='activo', required=True)
    alert_date = fields.Date(string="Fecha", required=True, default=fields.Date.context_today)
    group_alert = fields.Selection([('operation', 'Operaciones'),('invoice', 'Facturas')], default='operation', index=True, string='Grupo')