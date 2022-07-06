# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

#Estados del Viaje
T_STATES = [('draft','Borrador'),('planned','Planificado'),('programmed','Programado'),('started','En Curso'),('finished','Terminado'),('canceled','Cancelado')]

class TmsTravel(models.Model):
    _name = 'tms.travel'
    _description = 'Viaje'
    _order = "name desc"


    @api.depends('travel_route_ids.cost_ppto_cpy', 'travel_route_ids.cost_impt_cpy', 'travel_route_ids.cost_vigt_cpy', 'travel_route_ids')
    def _amount_all_vigente(self):
        """
        Obtener el costo vigente total del viaje
        """
        for op_travel in self:
            amount_cost_ppto_cpy = 0.0
            amount_cost_impt_cpy = 0.0
            amount_cost_vigt_cpy = 0.0
            for line in op_travel.travel_route_ids:
                amount_cost_ppto_cpy += line.cost_ppto_cpy
                amount_cost_impt_cpy += line.cost_impt_cpy
                amount_cost_vigt_cpy += line.cost_vigt_cpy
            op_travel.update({
                'cost_ppto_cpy': amount_cost_ppto_cpy,
                'cost_impt_cpy': amount_cost_impt_cpy,
                'cost_vigt_cpy': amount_cost_vigt_cpy,
            })

    name = fields.Char(string= 'Viaje', required=True, readonly=True, index=True, 
        states={'draft': [('readonly', False)]}, default='Nuevo')
    company_id = fields.Many2one('res.company', string="Empresa", default=lambda self: self.env.user.company_id)
    state = fields.Selection(T_STATES, readonly=True, String="Estado", index=True, default='draft')
    employee_operative = fields.Many2one('hr.employee', 'Personal Operativo', required=True)
    date = fields.Datetime('Fecha de registro', default=(fields.Datetime.now), readonly=True)
    #==================================================================================================
    date_start = fields.Datetime(string='Fecha Inicio', required=True, default=(fields.Datetime.now), Copy=False)
    date_end = fields.Datetime(string='Fecha Fin', required=True, copy=False)
    travel_duration = fields.Float(string='Duración (Hrs)',
        compute='_compute_travel_duration', help='Duración del viaje (Hrs).', readonly=True, store=True)
    #==================================================================================================
    date_start_real = fields.Datetime("Fecha Inicio Real", help='Inicio real del Viaje', readonly=True)
    date_end_real = fields.Datetime('Fecha Fin Real', help='Fin real del Viaje', readonly=True)
    travel_duration_real = fields.Float(string='Duración Real (Hrs)', 
        compute='_compute_travel_duration_real', help="Duración real del Viaje (Hrs).", readonly=True)
    travel_order = fields.Char(string='OV', readonly=True, index=True, 
        states={'draft': [('readonly', False)], 'planned': [('readonly', False)], 'programmed': [('readonly', False)], 'started': [('readonly', False)]})
    #==================================================================================================
    currency_id = fields.Many2one('res.currency', 'Moneda', required=True, default=lambda self: self.env.user.company_id.currency_id)
    cost_ppto_total = fields.Float(string='Costo Ppto Total',  default=0.0)
    cost_ppto_cpy = fields.Float(string='Costo Ppto Company', compute='_amount_all_vigente', store=True)
    cost_impt_cpy = fields.Float(string='Costo Imputado Company', compute='_amount_all_vigente', store=True)
    cost_vigt_cpy = fields.Float(string='Costo Vigente Company', compute='_amount_all_vigente', store=True)

    notes = fields.Text("Notas")
    advance_ids = fields.One2many('tms.advance', 'travel_id', string='Adelantos')
    #Asignar un viaje a muchas rutas
    travel_route_ids = fields.One2many('tms.travel.route', 'travel_id', string='Tramo de Viaje')
    #Asignar Muchos viajes a muchos SOL
    sale_order_line_ids = fields.Many2many('sale.order.line', 'sale_order_line_travel_rel', 'travel_id', 'sale_order_line_id', 
        string="Servicios", copy=False, readonly=False)
    #Asignar un viaje a muchas guias
    #guide_ids = fields.One2many('tms.guide', 'travel_id', string='Guias')
    #ini Tracking
    track_count = fields.Integer(string='conteo Track', compute='_tracking_count', copy=False)
    track_ids = fields.One2many('tms.tracking', 'travel_id')
    #fin Tracking

    def _tracking_count(self):
        for travel in self:
            tracking_ids = self.env['tms.tracking'].search([('travel_id', '=', self.id)])
            travel.track_count = len(tracking_ids)

    def action_view_tracking(self):
        trk_obj = self.env['tms.tracking'].search([('travel_id', '=', self.id)])
        trk_ids = []
        for each in trk_obj:
            trk_ids.append(each.id)
        view_id = self.env.ref('tms.open_view_tms_tracking_form').id

        if trk_ids:
            if len(trk_ids) <= 0:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tms.tracking',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': 'Seguimiento',
                    'res_id': trk_ids and trk_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', trk_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'tms.tracking',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': 'Seguimiento',
                    'res_id': trk_ids
                }

            return value

    @api.depends('date_start', 'date_end')
    def _compute_travel_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                start_date = rec.date_start
                end_date = rec.date_end
                difference = (end_date - start_date).total_seconds() / 60 / 60
                rec.travel_duration = difference

    @api.model
    def create(self, vals):
        if vals.get('name','Nuevo') == 'Nuevo':
            if 'company_id' in vals and vals['company_id']:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('tms.travel') or 'Nuevo'
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('tms.travel') or 'Nuevo'
        result = super(TmsTravel, self).create(vals)
        return result


    @api.depends('date_start_real', 'date_end_real')
    def _compute_travel_duration_real(self):
        for rec in self:
            if rec.date_start_real and rec.date_end_real:
                start_date = rec.date_start_real
                end_date = rec.date_end_real
                difference = (end_date - start_date).total_seconds() / 60 / 60
                rec.travel_duration_real = difference

    #================================ INI ESTADOS ================================
    #Planificado
    def action_planned(self):
        for rec in self:
            raise UserError(_("Ir a Operaciones \n asociada al Viaje: %s y clic en Planificar.") % self.name)
            #rec.state = "planned"

    #Programado
    def action_programmed(self):
        for rec in self:
            raise UserError(_("Ir a Operaciones \n asociada al Viaje: %s y clic en Programar.") % self.name)
            #rec.state = "programmed"

    #En curso
    def action_started(self):
        for rec in self:
            raise UserError(_("Ir a Operaciones \n asociada al Viaje: %s y clic En Curso.") % self.name)
            #rec.state = "started"
            #rec.date_start_real = fields.Datetime.now()

    #Terminado
    def action_finished(self):
        for rec in self:
            raise UserError(_("Ir a Operaciones \n asociada al Viaje: %s y clic en Terminado.") % self.name)
            #rec.state = "finished"
            #rec.date_end_real = fields.Datetime.now()

    #Cancelado
    def action_canceled(self):
        for rec in self:
            #Si el Viaje tiene estado Terminado, entonces no se debe Cancelar.
            if self.state == 'finished':
                raise ValidationError(_("No puede cancelar un Viaje en estado 'Terminado'."))
            #Buscamos si hay adelantos no cancelados, si lo hubiera no se puede cancelar el viaje
            advances = rec.advance_ids.search([
                ('state', '!=', 'cancel'),
                ('travel_id', '=', rec.id)])
            if len(advances) >= 1:
                raise ValidationError(_('No puede cancelar el viaje! \n Primero debe cancelar el Adelanto.'))

            #Validamos que no este Terminado ni Cancelado
            if rec.state != 'finished' and rec.state != 'canceled':
                #Validamos que exista al menos una Operación sin Terminado o Cancelado.
                reg_operacion = self.env['tms.route.operation'].search([('travel_id','=', rec.id), ('state','not in', ('canceled', 'finished') )])
                if reg_operacion:
                    reg_operacion.write({'state': 'canceled'})
                #Si el tramo esta en Borrador, entonces se procede tambien a Cancelarlo.
                reg_tramo = self.env['tms.travel.route'].search([('travel_id','=', rec.id), ('state','=', ('draft'))])
                if reg_tramo:
                    reg_tramo.write({'state': 'cancel'})
            else:
                raise ValidationError(_('No puede cancelar el viaje! \n por estar en estado Terminado/Finalizado'))

            rec.date_end_real = fields.Datetime.now()
            rec.state = "canceled"

    #================================ FIN ESTADOS ================================

    #@api.multi
    #def button_add_sol_travel(self):
    #    return {
    #        'name': 'Asociar Servicios',
    #        'view_mode': 'tree',
    #        'view_type': 'form',
    #        'res_model': 'sale.order.line',
    #        'type': 'ir.actions.act_window',
    #        'domain': [('is_travel', '=', True)],
    #        'target': 'current'
    #    }