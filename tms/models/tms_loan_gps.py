# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime

class TmsLoanGps(models.Model):
    _name = 'tms.loan.gps'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Prestamo de GPS'
    _order = "name desc"

    name = fields.Char(string= 'Prestamo GPS', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    travel_id = fields.Many2one('tms.travel', required=True, string='Viaje')
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('loan', 'Prestado'),
         ('return', 'Devuelto'),
         ('cancel', 'Cancelado')],
        readonly=True, default='draft', index=True, string='Estado')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehículo')
    vehicle_outsourcing= fields.Boolean(related="vehicle_id.outsourcing", string='Tercerizado?', help='Indica si el vehículo es Tercerizado')
    vehicle_type_id = fields.Many2one(related="vehicle_id.vehicle_type_id", string='Tipo de Vehículo', store=True)
    vendor_id = fields.Many2one(related="vehicle_id.partner_id", string="Proveedor",  store=True)
    driver_id = fields.Many2one('hr.employee', string='Conductor', compute='_compute_driver_id', store=True)
    telf_driver = fields.Char(related="driver_id.mobile_phone",string='Telf', required=True, index=True)
    device_gps_id = fields.Many2one('tms.gps', string='Dispositivo GPS')
    platform_gps = fields.Char(related="device_gps_id.platform_gps", string= 'Plataforma GPS', index=True, store=True, readonly=True)
    user_name = fields.Char(related="device_gps_id.user_name", string= 'Usuario', store=True, readonly=True)
    password = fields.Char(related="device_gps_id.password", string= 'Password', store=True, readonly=True)
    date_loan = fields.Date(string='Fecha de Préstamo')
    days_to_loan = fields.Integer(compute='_compute_days_to_loan', string='Días de Préstamo')
    notes = fields.Text("Notas")


    @api.depends('vehicle_id')
    def _compute_driver_id(self):
        for rec in self:
            rec.driver_id = rec.vehicle_id.employee_driver_id


    @api.depends('date_loan')
    def _compute_days_to_loan(self):
        for rec in self:
            now = datetime.now()
            date_ini = datetime.strptime(
                rec.date_loan,
                '%Y-%m-%d') if rec.date_loan else datetime.now()
            delta = now - date_ini
            if delta.days >= 0 and rec.date_loan :
                rec.days_to_loan = delta.days
            else:
                rec.days_to_loan = 0

    @api.model
    def create(self, vals):        
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.loan.gps') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.loan.gps') or 'Nuevo'
        result = super(TmsLoanGps, self).create(vals)
        return result


    def action_loan(self):
        for rec in self:
            #Validamos que no este en otro prestamo
            if rec.device_gps_id.in_loan == True:
                raise ValidationError(_("El GPS '%s' ya esta tomado en otro préstamo!") % (rec.device_gps_id.name))
            else:
                rec.state = 'loan'
                #Actualiza el prestamo del GPS
                rec.device_gps_id.in_loan = True

    def action_cancel(self):
        for rec in self:
            if rec.state == 'return':
                raise ValidationError(_("No se puede cancelar un préstamo en estado 'Devuelto'"))
            else:
                rec.state = 'cancel'

    def action_return(self):
        for rec in self:
            rec.state = 'return'
            #Actualiza el prestamo del GPS
            rec.device_gps_id.in_loan = False

