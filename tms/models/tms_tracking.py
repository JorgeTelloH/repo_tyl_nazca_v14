# -*- coding: utf-8 -*-

from odoo import models, fields, api

#Colores
color_green='#49C909'

class TmsTracking(models.Model):
    _name = 'tms.tracking'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Tracking de Operaciones en el viaje'
    _order = "date desc"

    name = fields.Char(string= 'Seguimiento', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    route_operation_id = fields.Many2one('tms.route.operation', string='Operación TMS', required=True, index=True,
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    operation_type_id = fields.Many2one(related="route_operation_id.operation_type", string='Tipo de Operación', readonly=True, store=True)
    travel_route_id = fields.Many2one(related="route_operation_id.travel_route_id", string='Tramo de Viaje', readonly=True, store=True)
    travel_id = fields.Many2one(related="route_operation_id.travel_id", string='Viaje', readonly=True, store=True)
    date = fields.Datetime(string='Fecha y Hora', default=(fields.Datetime.now), required=True,
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    type_tracking = fields.Selection(
        [('tracking', 'Seguimiento'),
         ('incidence', 'Incidencia')], default='tracking', required=True, string='Tipo',
         states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    status_track = fields.Many2one('tms.status.track', string='Estado de Seguimiento', required=True,
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('confirm', 'Confirmado'),
         ('cancel', 'Anulado')], readonly=True, default='draft', string='Estado')
    notes = fields.Text(string='Observación',
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    latitude = fields.Char(string='Latitud',
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    longitude = fields.Char(string='Longitud',
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    position_real = fields.Text(string='Posición Real', help="Posición del GPS",
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    track_img = fields.Binary(string='Imagen', attachment=True, store=True,
        states={'confirm': [('readonly', True)], 'cancel': [('readonly', True)]})
    #Campos agregados a pedido de Trafico
    travel_operative = fields.Many2one(related="route_operation_id.travel_operative", string='Coordinador', readonly=True, store=True)
    vendor_id = fields.Many2one(related="route_operation_id.vendor_id", string='Proveedor', readonly=True, store=True)
    driver_id = fields.Many2one(related="route_operation_id.driver_id", string='Conductor', readonly=True, store=True)

    @api.model
    def create(self, vals):
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.tracking') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.tracking') or 'Nuevo'
        vals['state'] = 'confirm'

        result = super(TmsTracking, self).create(vals)
        result.route_operation_id.date_track = fields.Datetime.now()
        #Actualiza el color del semaforo
        result.route_operation_id.traffic_light = color_green
        return result

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def set_2_draft(self):
        for rec in self:
            rec.state = 'draft'

    #Cuando se grabe la data, esta pase de Borrador a Confirmado
    #@api.model
    #def create(self, vals):
    #    vals['state'] = 'confirm'
    #    res = super(TmsTracking, self).create(vals)
    #    return res