# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _order = 'name'

    employee_driver_id = fields.Many2one('hr.employee', string="Conductor", domain=[('driver', '=', True)])
    partner_id = fields.Many2one('res.partner', string='Proveedor', index=True, help='Proveedor del vehículo')
    outsourcing = fields.Boolean(string='Unidad de Tercero?', default=False, help='Activar si el vehículo es Tercerizado')
    unit_complement = fields.Boolean(string='Unidad Carreta?', default=False,
        help='Activar si es una Unidad Carreta')
    engine_nbr = fields.Char(string='Nro motor')
    notes = fields.Text()
    insurance_policy_nbr = fields.Char(string='Nro Póliza')
    insurance_supplier_id = fields.Many2one('res.partner', string='Proveedor de seguro')
    insurance_expedition = fields.Date(string='Fecha desde', help='Fecha inicio de vigencia de Póliza')
    insurance_expiration = fields.Date(string='Fecha hasta', help='Fecha fin de vigencia de Póliza')
    insurance_days_to_expire = fields.Integer(compute='_compute_insurance_days_to_expire', string='Días de caducidad')
    insurance_policy_file = fields.Many2many('ir.attachment','vehicle_policy_attachment_rel', 'vehicle_id','attachment_id', string='Archivo(s)')
    habilitation_nbr = fields.Char(string='Nro Certificado')
    habilitation_expedition = fields.Date(string='Fecha de Expedición')
    habilitation_expiration = fields.Date(string='Fecha de Vencimiento')
    habilitation_days_to_expire = fields.Integer(compute='_compute_habilitation_days_to_expire', string='Días de caducidad')
    habilitation_file = fields.Many2many('ir.attachment', 'vehicle_habili_attachment_rel', 'vehicle_id','attachment_id', string='Archivo(s)')
    inspection_nbr = fields.Char(string='Nro Certificado')
    inspection_expedition = fields.Date(string='Fecha de Expedición')
    inspection_expiration = fields.Date(string='Fecha de Vencimiento')
    inspection_days_to_expire = fields.Integer(compute='_compute_inspection_days_to_expire', string='Días de caducidad')
    inspection_file = fields.Many2many('ir.attachment', 'vehicle_inspection_attachment_rel', 'vehicle_id','attachment_id', string='Archivo(s)')



    @api.depends('insurance_expiration')
    def _compute_insurance_days_to_expire(self):
        for rec in self:
            now = datetime.now()
            date_expire = datetime.strptime(
                rec.insurance_expiration,
                '%Y-%m-%d') if rec.insurance_expiration else datetime.now()
            delta = date_expire - now
            if delta.days >= 0 and rec.insurance_expiration :
                rec.insurance_days_to_expire = delta.days + 1
            else:
                rec.insurance_days_to_expire = 0

    @api.depends('habilitation_expiration')
    def _compute_habilitation_days_to_expire(self):
        for rec in self:
            now2 = datetime.now()
            date_expire2 = datetime.strptime(
                rec.habilitation_expiration,
                '%Y-%m-%d') if rec.habilitation_expiration else datetime.now()
            delta2 = date_expire2 - now2
            if delta2.days >= 0 and rec.habilitation_expiration :
                rec.habilitation_days_to_expire = delta2.days + 1
            else:
                rec.habilitation_days_to_expire = 0

    @api.depends('inspection_expiration')
    def _compute_inspection_days_to_expire(self):
        for rec in self:
            now3 = datetime.now()
            date_expire3 = datetime.strptime(
                rec.inspection_expiration,
                '%Y-%m-%d') if rec.inspection_expiration else datetime.now()
            delta3 = date_expire3 - now3
            if delta3.days >= 0 and rec.inspection_expiration :
                rec.inspection_days_to_expire = delta3.days + 1
            else:
                rec.inspection_days_to_expire = 0

