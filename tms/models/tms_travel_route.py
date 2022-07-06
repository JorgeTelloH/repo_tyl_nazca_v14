# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TmsTravelRoute(models.Model):
    _name = 'tms.travel.route'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Tramo del Viaje'
    _order = "name desc"


    @api.depends('route_operation_ids.cost_ppto_cpy', 'route_operation_ids.cost_impt_cpy', 'route_operation_ids.cost_vigt_cpy', 'route_operation_ids')
    def _amount_all_vigente(self):
        """
        Obtener el monto Vigente company de las Operaciones
        """
        for operation1 in self:
            amount_cost_ppto_cpy = 0.0
            amount_cost_impt_cpy = 0.0
            amount_cost_vigt_cpy = 0.0
            v_monto_vig_cpy_check_impt = 0.0
            v_cuenta_reg = 0
            v_cuenta_impt = 0
            v_check_impt = False
            for line in operation1.route_operation_ids:
                amount_cost_ppto_cpy += line.cost_ppto_cpy
                amount_cost_impt_cpy += line.cost_impt_cpy
                amount_cost_vigt_cpy += line.cost_vigt_cpy

                if line.state != 'canceled':
                    v_cuenta_reg = v_cuenta_reg + 1
                    if line.check_impt == True:
                        v_cuenta_impt = v_cuenta_impt + 1
                        v_monto_vig_cpy_check_impt = v_monto_vig_cpy_check_impt + line.cost_impt_cpy
            if v_cuenta_reg > 0:
                if v_cuenta_reg == v_cuenta_impt:
                    v_check_impt = True

            operation1.update({
                'cost_ppto_cpy': amount_cost_ppto_cpy,
                'cost_impt_cpy': amount_cost_impt_cpy,
                'cost_vigt_cpy': amount_cost_vigt_cpy,
                'check_impt': v_check_impt,
                'cost_vigt_cpy_check_impt': v_monto_vig_cpy_check_impt, 
            })

    name = fields.Char(string= 'Id Tramo', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    travel_id = fields.Many2one('tms.travel', string='Viaje', required=True)
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmado'),
        ('cancel', 'Anulado')],
        readonly=True, String="Estado", index=True, default='draft')
    departure_id = fields.Many2one('tms.place', 'Salida', required=True)
    orig_district_id = fields.Many2one(related='departure_id.district_id', store=True, string='Dist Origen')
    arrival_id = fields.Many2one('tms.place', 'Llegada', required=True)
    dest_district_id = fields.Many2one(related='arrival_id.district_id', store=True, string='Dist Destino')
    distance_route = fields.Float('Distancia (Kms)', digits=(14, 4), help='Distancia del Tramo (Kms)')
    travel_time = fields.Float('Tiempo (Hrs)', digits=(14, 4), help='Tiempo del Tramo (Hrs)', required=True)
    date_start = fields.Datetime(string='Fecha Inicio')
    date_end = fields.Datetime(string='Fecha Fin',
        compute='_compute_date_end', store=True)
    route_load = fields.Boolean('Tramo con Carga', default=True)
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, default=lambda self: self.env.user.company_id.currency_id)
    cost_ppto_total = fields.Float('Costo Ppto Total', default=0.0)
    notes = fields.Text(string='Notas')
    route_closed = fields.Boolean(string="Tramo cerrado", default=False, help='Se activa automáticamente al Finalizar o Cancelar el Viaje.', 
        compute='_compute_route_close', store=True, readonly=True)
    route_operation_ids = fields.One2many('tms.route.operation', 'travel_route_id', string='Operaciones por Tramo', copy=True, auto_join=True)
    travel_route_service_ids = fields.One2many('tms.travel.route.service', 'travel_route_id', string='Lineas de Servicio', copy=True, auto_join=True)
    cost_ppto_cpy = fields.Float(string='Costo Ppto Company', compute='_amount_all_vigente', store=True)
    cost_impt_cpy = fields.Float(string='Costo Imputado Company', compute='_amount_all_vigente', store=True)
    cost_vigt_cpy = fields.Float(string='Costo Vigente Company', compute='_amount_all_vigente', store=True)
    prc_advance_impt = fields.Float(string='Porc Avance Imputación - No usar')
    check_impt = fields.Boolean(String='Imputado', compute='_amount_all_vigente', store=True)
    cost_vigt_cpy_check_impt = fields.Float(string='Costo Vigente Company Imputado', compute='_amount_all_vigente', store=True)
    prc_avance_impt = fields.Float(string='Porc Avance Imputado', compute='_find_prc_avance_impt', store=True)

    #Obtener Porcentaje de Avance Imputado
    @api.depends('cost_vigt_cpy_check_impt')
    def _find_prc_avance_impt(self):
        for travel in self:
            v_avance_impt = 0
            if travel.cost_vigt_cpy != 0:
                v_avance_impt = ((travel.cost_vigt_cpy_check_impt * 100) / travel.cost_vigt_cpy)
            travel.prc_avance_impt = v_avance_impt

    @api.depends('travel_id.state', 'state')
    def _compute_route_close(self):
        """
        Si el tramo se cancela o el estado del viaje es finalizado/cancelado, entonces actualizar el Tramo
        """
        for travel in self:
            if travel.state == 'cancel':
                travel.route_closed = True
            elif travel.travel_id.state == 'finished' or travel.travel_id.state == 'canceled':
                travel.route_closed = True
            else:
                travel.route_closed = False

    @api.depends('date_start')
    def _compute_date_end(self):
        for rec in self:
            if rec.date_start:
                strp_date = rec.date_start
                rec.date_end = strp_date + timedelta(hours=rec.travel_time)

    @api.model
    def create(self, vals):        
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.travel.route') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.travel.route') or 'Nuevo'
        result = super(TmsTravelRoute, self).create(vals)
        return result

    def action_cancel(self):
        for rec in self:
            if (rec.travel_id and rec.travel_id.state == 'started'):
                raise ValidationError(_('No puedes cancelar un Tramo asignado a un Viaje En Curso!'))
            if (rec.travel_id and rec.travel_id.state == 'finished'):
                raise ValidationError(_('No puedes cancelar un Tramo asignado a un Viaje Terminado!'))

            oper_obj = self.env['tms.route.operation'].search([('travel_route_id', '=', self.id),('state', '!=', 'canceled')])
            if oper_obj:
                raise ValidationError(_(
                    "No puedes cancelar un Tramo con Operación asignada.\n"
                    "Debe cancelar la(s) Operacion(es) asignad(as)."))

            if rec.travel_route_service_ids:
                raise ValidationError(_(
                    "No puedes cancelar un Tramo con Orden de Servicio asignada.\n "
                    "Debes cancelar la Orden de Servicio desde el Viaje del Tramo."))

            rec.state = 'cancel'

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def set_2_draft(self):
        for rec in self:
            rec.state = 'draft'
