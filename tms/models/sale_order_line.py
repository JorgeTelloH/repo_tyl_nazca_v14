# -*- coding: utf-8 -*-

#import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#_logger = logging.getLogger(__name__)
#Tipo de Envio
S_TYPE = [('exclusivo', 'Exclusivo'),('consolidado', 'Consolidado')]

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('travel_route_service_ids.w_cost_ppto_cpy', 'travel_route_service_ids.w_cost_impt_cpy', 'travel_route_service_ids.w_cost_vigt_cpy', 'travel_route_service_ids')
    def _amount_all_tramos(self):
        """
        Obtener los costos de los tramos del viaje
        """
        for sol_tramo in self:
            amount_cost_ppto_cpy = 0.0
            amount_cost_impt_cpy = 0.0
            amount_cost_vigt_cpy = 0.0
            v_monto_vig_cpy_check_impt = 0.0
            v_cuenta_reg = 0
            v_cuenta_impt = 0
            v_check_impt = False
            for line in sol_tramo.travel_route_service_ids:
                amount_cost_ppto_cpy += line.w_cost_ppto_cpy
                amount_cost_impt_cpy += line.w_cost_impt_cpy
                amount_cost_vigt_cpy += line.w_cost_vigt_cpy
                v_monto_vig_cpy_check_impt += line.w_cost_vigt_cpy_check_impt
                v_cuenta_reg = v_cuenta_reg + 1
                if line.check_impt == True:
                    v_cuenta_impt = v_cuenta_impt + 1
            if v_cuenta_reg > 0:
                if v_cuenta_reg == v_cuenta_impt:
                    v_check_impt = True

            if sol_tramo.currency_id == sol_tramo.company_id.currency_id:
                v_cost_ppto_operation = amount_cost_ppto_cpy
                v_cost_impt = amount_cost_impt_cpy
                v_cost_vigt = amount_cost_vigt_cpy

            else:
                #Pasamos de la moneda Company a moneda Extranjera
                try:
                    #v_cost_ppto_operation = self.env['res.currency']._compute(sol_tramo.company_id.currency_id, sol_tramo.currency_id, amount_cost_ppto_cpy)
                    v_cost_ppto_operation = sol_tramo.company_id.currency_id.convert(amount_cost_ppto_cpy, sol_tramo.currency_id,
                                                              sol_tramo.company_id, fields.Date.today())
                except ZeroDivisionError:
                    v_cost_ppto_operation = 0.0

                try:
                    #v_cost_impt = self.env['res.currency']._compute(sol_tramo.company_id.currency_id, sol_tramo.currency_id, amount_cost_impt_cpy)
                    v_cost_impt = sol_tramo.company_id.currency_id.convert(amount_cost_impt_cpy,
                                                                                     sol_tramo.currency_id,
                                                                                     sol_tramo.company_id,
                                                                                     fields.Date.today())
                except ZeroDivisionError:
                    v_cost_impt = 0.0

                try:
                    #v_cost_vigt = self.env['res.currency']._compute(sol_tramo.company_id.currency_id, sol_tramo.currency_id, amount_cost_vigt_cpy)
                    v_cost_vigt = sol_tramo.company_id.currency_id.convert(amount_cost_vigt_cpy,
                                                                           sol_tramo.currency_id,
                                                                           sol_tramo.company_id,
                                                                           fields.Date.today())
                except ZeroDivisionError:
                    v_cost_vigt = 0.0

            sol_tramo.update({
                'cost_ppto_cpy': amount_cost_ppto_cpy,
                'cost_ppto_operation': v_cost_ppto_operation,
                'cost_impt_cpy': amount_cost_impt_cpy,
                'cost_impt': v_cost_impt,
                'cost_vigt_cpy': amount_cost_vigt_cpy,
                'cost_vigt': v_cost_vigt,
                'check_impt': v_check_impt,
                'cost_vigt_cpy_check_impt': v_monto_vig_cpy_check_impt,
            })


    order_operative_id = fields.Many2one(related='order_id.employee_operative', store=True, string='Personal Operativo')
    appt_start = fields.Datetime(string='Fecha Hora Inicio', index=True)
    appt_end = fields.Datetime(string='Fecha Hora Fin')
    is_travel = fields.Boolean(string='Es un Viaje?', compute='_compute_is_travel', store=True)
    vehicle_type_id = fields.Many2one(related='product_id.vehicle_type_id', store=True, string='Tipo de vehículo')
    load_capacity_id = fields.Many2one(related='product_id.load_capacity_id', store=True, string='Capacidad')
    load_type_id = fields.Many2one('tms.load.type', string='Tipo de Mercadería')
    orig_place = fields.Char(string='Origen', compute='_compute_origen', store=True)
    orig_district_id = fields.Many2one(related='product_id.orig_district', store=True, string='Dist Origen')
    dest_place = fields.Char(string='Destino', compute='_compute_destino', store=True)
    dest_district_id = fields.Many2one(related='product_id.dest_district', store=True, string='Dist Destino')
    send_type = fields.Selection(S_TYPE, default='exclusivo', index=True, string='Tipo Envío')
    guide_nbr = fields.Text("Guias")
    check_pending = fields.Boolean(string='SOL Pendiente', default=False)
    check_assigned = fields.Boolean(string='SOL Asignado', default=False, copy=False)
    #travel_id = fields.Many2one('tms.travel', string='Viaje', required=True)
    cst_ppto_flete = fields.Float(string='Costo Flete', default=0.0)
    cst_ppto_carga = fields.Float(string='Costo Carga', default=0.0)
    cst_ppto_descarga = fields.Float(string='Costo Descarga', default=0.0)
    cst_ppto_resguardo = fields.Float(string='Costo Resguardo', default=0.0)
    cst_ppto_otros = fields.Float(string='Costo Otros', default=0.0)
    #Costo esperado = costo flete + carga + descarga + resguardo + otros
    cst_ppto_expected = fields.Float(compute ='get_sum_cst_ppto', store=True, readonly=True, string='Costo Esperado')
    cst_ppto_expected_cpy = fields.Float(compute ='get_sum_cst_ppto', store=True, readonly=True, string='Costo Esperado Company')
    expected_margin = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Margen Esperado')
    expected_margin_cpy = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Margen Esperado Company')
    prc_expected_margin = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Porc Margen Esperado')
    company_currency_amount_untaxed = fields.Float(string='Subtotal Company', compute='_find_amount_untaxed_company', store=True)
    travel_ids = fields.Many2many('tms.travel', 'sale_order_line_travel_rel', 'sale_order_line_id', 'travel_id', string="Viaje", copy=False)
    cost_ppto_cpy = fields.Float(string='Costo Ppto Company', compute='_amount_all_tramos', store=True, copy=False)
    cost_impt_cpy = fields.Float(string='Costo Imputado Company', compute='_amount_all_tramos', store=True, copy=False)
    cost_vigt_cpy = fields.Float(string='Costo Vigente Company', compute='_amount_all_tramos', store=True, copy=False)
    prc_advance_impt = fields.Float(string='Porc Avance Imputación - No usar')
    check_impt = fields.Boolean(String='Imputado', compute='_amount_all_tramos', store=True, copy=False)
    cost_vigt_cpy_check_impt = fields.Float(string='Costo Vigente Company Imputado', compute='_amount_all_tramos', store=True, copy=False)
    prc_avance_impt = fields.Float(string='Porc Avance Imputado', compute='_find_prc_avance_impt', store=True, copy=False)
    travel_route_service_ids = fields.One2many('tms.travel.route.service', 'sale_order_line_id', string='Lineas de Tramos', copy=False, auto_join=True)
    date_order = fields.Date(related='order_id.date_order', store=True, string='Fecha Pedido')
    #Costos en Moneda de la Venta
    cost_ppto_operation = fields.Float(string='Costo Operacional', compute='_amount_all_tramos', store=True, copy=False)
    cost_impt = fields.Float(string='Costo Imputado', compute='_amount_all_tramos', store=True, copy=False)
    cost_vigt = fields.Float(string='Costo Vigente', compute='_amount_all_tramos', store=True, copy=False)
    #Costos Esperados Adicionales
    cst_ppto_cabinero = fields.Float(string='Costo Cabinero', default=0.0)
    cst_ppto_merma = fields.Float(string='Costo Merma', default=0.0)
    cst_ppto_sobrestadia = fields.Float(string='Costo Sobrestadia', default=0.0)
    cst_ppto_fflete = fields.Float(string='Costo Falso Flete', default=0.0)
    cst_ppto_policial = fields.Float(string='Costo Apoyo Policial', default=0.0)

    #Obtener Porcentaje de Avance Imputado
    @api.depends('cost_vigt_cpy_check_impt')
    def _find_prc_avance_impt(self):
        for ol in self:
            v_avance_impt = 0.0
            if ol.cost_vigt_cpy != 0:
                v_avance_impt = ((ol.cost_vigt_cpy_check_impt * 100) / ol.cost_vigt_cpy)
            ol.prc_avance_impt = v_avance_impt

    #Obtener el Margen Esperado (Venta sin impuestos - Costo Esperado)
    @api.depends('cst_ppto_expected', 'price_subtotal')
    def _compute_expected_margin(self):
        for ol in self:
            v_expected_margin = ol.price_subtotal - ol.cst_ppto_expected

            if ol.price_subtotal == 0.0:
                v_subtotal = 1
            else:
                v_subtotal = ol.price_subtotal

            if ol.currency_id == ol.company_id.currency_id:
                v_expected_margin_cpy = v_expected_margin
            else:
                #Se agrega control de error de division con cero
                try:
                    #v_expected_margin_cpy = self.env['res.currency']._compute(ol.currency_id, ol.company_id.currency_id, v_expected_margin)
                    v_expected_margin_cpy = ol.currency_id.convert(v_expected_margin,
                                                         ol.company_id.currency_id,
                                                         ol.company_id,
                                                         fields.Date.today())
                except ZeroDivisionError:
                    v_expected_margin_cpy = 0.0

            ol.prc_expected_margin = round(((v_expected_margin * 100) / v_subtotal),2)
            ol.expected_margin = v_expected_margin
            ol.expected_margin_cpy = v_expected_margin_cpy

    #Obtener el Subtotal Company
    @api.depends('price_subtotal', 'state')
    def _find_amount_untaxed_company(self):
        for order in self:
            if order.currency_id == order.company_id.currency_id:
                price_untaxed = order.price_subtotal
            else:
                #Se agrega control de error de division con cero
                try:
                    #price_untaxed = self.env['res.currency']._compute(order.currency_id, order.company_id.currency_id, order.price_subtotal)
                    price_untaxed = order.currency_id.convert(order.price_subtotal,
                                                                   order.company_id.currency_id,
                                                                   order.company_id,
                                                                   fields.Date.today())
                except ZeroDivisionError:
                    price_untaxed = 0.0
            order.company_currency_amount_untaxed = price_untaxed

    #Suma total de costo ppto del Comercial
    @api.depends('cst_ppto_flete', 'cst_ppto_carga', 'cst_ppto_descarga', 'cst_ppto_resguardo', 'cst_ppto_otros',
    	'cst_ppto_cabinero', 'cst_ppto_merma', 'cst_ppto_sobrestadia', 'cst_ppto_fflete', 'cst_ppto_policial')
    def get_sum_cst_ppto(self):
        for line in self:
            cst_expected = 0
            for sum_cst in [line.cst_ppto_flete, line.cst_ppto_carga, line.cst_ppto_descarga, line.cst_ppto_resguardo , line.cst_ppto_otros,
                            line.cst_ppto_cabinero, line.cst_ppto_merma, line.cst_ppto_sobrestadia, line.cst_ppto_fflete, line.cst_ppto_policial]:
                cst_expected = cst_expected + sum_cst
            line.cst_ppto_expected = cst_expected

            if line.currency_id == line.company_id.currency_id:
                v_cst_ppto_expected_cpy = cst_expected
            else:
                #Se agrega control de error de division con cero
                try:
                    #v_cst_ppto_expected_cpy = self.env['res.currency']._compute(self.currency_id, self.company_id.currency_id, cst_expected)
                    v_cst_ppto_expected_cpy = line.currency_id.convert(cst_expected,
                                                              line.company_id.currency_id,
                                                              line.company_id,
                                                              fields.Date.today())
                except ZeroDivisionError:
                    v_cst_ppto_expected_cpy = 0.0
            line.cst_ppto_expected_cpy = v_cst_ppto_expected_cpy

    #Validar que la fecha inicio sea menor o igual a la fecha fin
    @api.constrains('appt_start', 'appt_end')
    def _check_start_end_dates(self):
        if (self.appt_start and self.appt_end and
                self.appt_start > self.appt_end):
            raise ValidationError(_(
                    "Fecha/Hora Inicio debe ser menor o igual "
                    "a la Fecha/Hora Fin - Item '%s'.") % (self.product_id.name))

    #Obtener si el producto es viaje
    @api.depends('product_id')
    def _compute_is_travel(self):
        for rec in self:
            rec.is_travel = rec.product_id.is_travel

    #Obtener origen del viaje
    @api.depends('product_id')
    def _compute_origen(self):
        for rec in self:
            rec.orig_place = rec.product_id.orig_place

    #Obtener destino del viaje
    @api.depends('product_id')
    def _compute_destino(self):
        for rec in self:
            rec.dest_place = rec.product_id.dest_place

    def action_desasignar_sol_travel(self):
        # Id SO
        #v_order_id = self.order_id.id
        # Id SOL
        v_sol_id = self.id

        #Eliminar Relacion SOL con Tramo
        route_service_object = self.env['tms.travel.route.service'].search([('sale_order_line_id', '=',v_sol_id)])

        #Validar que tiene Viaje en Borrador o Anulado para Desasignar
        if route_service_object:
            for travel_serv in route_service_object:
                if travel_serv.travel_route_id.travel_id.state not in ('draft','canceled'):
                    raise ValidationError(_(
                        "El Viaje: '%s' debe estar en Borrador o Anulado para desasignar")%(travel_serv.travel_route_id.travel_id.name))

        # ini procedemos a obtener los ID de Tramo antes del unlink ---proceso 01
        v_tramos = []
        v_len = 0
        #Obtener mediante query obtenemos los tramos
        query = """SELECT b.travel_route_id
                    FROM tms_travel_route_service b 
                    where """
        query += " b.sale_order_line_id = %s " % (v_sol_id)
        query += "  group by b.travel_route_id"

        self.env.cr.execute(query)
        data_tramo = self.env.cr.fetchall() or False

        if data_tramo:
            for line in data_tramo:
                v_tramos += ''.join([str(col) for col in line]) + ', '
            
            v_len = len(v_tramos)
            if v_len > 1:
                v_len = v_len - 2
                v_tramos = v_tramos[0:v_len]
        # fin procedemos a obtener los ID de Tramo antes del unlink ---proceso 01

        #procedemos a eliminar el SOl de los tramos
        route_service_object.unlink()

        for records1 in v_tramos:
            # ini procedemos a recalcular los IDS de tramos ---proceso 02
            #============================================================
            d_sol_subtotal = self.env['tms.travel.route.service'].search([('travel_route_id', '=', int(records1) )])
            #Proceso 01
            v_sum_sol_subtotal = 0
            if d_sol_subtotal:
                for records in d_sol_subtotal:
                    #Obtenemos los subtotales de todos los SOL del tramo seleccionado
                    v_sum_sol_subtotal = v_sum_sol_subtotal + records.sol_amount_untaxed_cpy
            #Proceso 02
            if d_sol_subtotal:

                for records2 in d_sol_subtotal:
                    if v_sum_sol_subtotal == 0:
                        v_sum_sol_subtotal = 1

                    v_porc_sol_subtotal = round(((records2.sol_amount_untaxed_cpy * 100) / v_sum_sol_subtotal ),2)
                    v_w_cost_ppto_cpy = round(((records2.travel_route_id.cost_ppto_cpy * v_porc_sol_subtotal ) / 100),2)
                    v_w_cost_impt_cpy = round(((records2.travel_route_id.cost_impt_cpy * v_porc_sol_subtotal ) / 100),2)
                    v_w_cost_vigt_cpy = round(((records2.travel_route_id.cost_vigt_cpy * v_porc_sol_subtotal ) / 100),2)
                    v_w_cost_vigt_cpy_check_impt = round(((self.travel_route_id.cost_vigt_cpy_check_impt * v_porc_sol_subtotal ) / 100),2)
                    v_check_impt = self.travel_route_id.check_impt
                    v_prc_avance_impt = self.travel_route_id.prc_avance_impt
                    sol_route_line_dict ={
                                  'porc_sol_subtotal': v_porc_sol_subtotal,
                                  'w_cost_ppto_cpy': v_w_cost_ppto_cpy,
                                  'w_cost_impt_cpy': v_w_cost_impt_cpy,
                                  'w_cost_vigt_cpy': v_w_cost_vigt_cpy,
                                  'w_cost_vigt_cpy_check_impt': v_w_cost_vigt_cpy_check_impt,
                                  'check_impt': v_check_impt,
                                  'prc_avance_impt': v_prc_avance_impt,
                                  }
                    records2.update(sol_route_line_dict)
            #============================================================
            # fin procedemos a recalcular los IDS de tramos ---proceso 02

        #Eliminar Relacion SOL con Viaje
        query = """DELETE 
                    FROM sale_order_line_travel_rel"""
        query += " where sale_order_line_id = %s " % (v_sol_id)
        self.env.cr.execute(query)

        #actualizar el campo asignado en SOL
        sol_obj = self.env['sale.order.line'].search([('id', '=',v_sol_id)])
        update_sol = {'check_assigned': False}
        sol_obj.write(update_sol)
        #query = """UPDATE 
        #           sale_order_line SET check_assigned = False"""
        #query += " WHERE id = %s " % (v_sol_id)
        #self.env.cr.execute(query)

        #Ini Mensaje
        v_msg = ("Se Desasignó el Servicio con el Tramo-Viaje.")
        view = self.env.ref('sh_message.sh_message_wizard')
        view_id = view and view.id or False
        context = dict(self._context or {})
        context['message']= v_msg
        return {
            'name': 'Desasignar Servicio',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views':[(view.id,'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
            }
        #Fin Mensaje
