# -*- coding: utf-8 -*-

#import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#_logger = logging.getLogger(__name__)

class TmsTravelRouteService(models.Model):
    _name = 'tms.travel.route.service'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Servicio asociado al Tramo del Viaje'

    name = fields.Char(string= 'Descripción')
    travel_route_id = fields.Many2one('tms.travel.route', string='Tramo de Viaje', required=True, index=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Servicios', required=True, index=True)
    order_id = fields.Many2one(related="sale_order_line_id.order_id", string='Servicio', readonly=True)
    order_partner_id = fields.Many2one(related="sale_order_line_id.order_partner_id", string='Cliente', readonly=True)
    appt_start = fields.Datetime(related="sale_order_line_id.appt_start", string='Fecha Hora Inicio', readonly=True)
    appt_end = fields.Datetime(related="sale_order_line_id.appt_end", string='Fecha Hora Fin', readonly=True)
    orig_place = fields.Char(related="sale_order_line_id.orig_place", string='Origen', readonly=True)
    dest_place = fields.Char(related="sale_order_line_id.dest_place", string='Destino', readonly=True)
    vehicle_type_id = fields.Many2one(related='sale_order_line_id.vehicle_type_id', string='Tipo de vehículo', readonly=True)
    load_capacity_id = fields.Many2one(related='sale_order_line_id.load_capacity_id', string='Capacidad', readonly=True)
    load_type_id = fields.Many2one(related='sale_order_line_id.load_type_id', string='Tipo de Mercadería', readonly=True)
    product_uom_qty = fields.Float(related='sale_order_line_id.product_uom_qty', string='Cantidad', readonly=True)
    guide_nbr = fields.Text(related='sale_order_line_id.guide_nbr', string="Guias", readonly=True)
    b_start_trip =fields.Boolean(string='Subida', default=False)
    b_continue_trip = fields.Boolean(string='Continua', default=False)
    b_end_trip = fields.Boolean(string='Bajada', default=False)
    sol_amount_untaxed_cpy = fields.Float(related='sale_order_line_id.company_currency_amount_untaxed',  string='Subtotal Company de Linea de Pedido', store=True)
    porc_sol_subtotal = fields.Float(string='Porcentaje Linea de Pedido', compute='_calc_cost_weighted_route', store=True)
    w_cost_ppto_cpy = fields.Float(string='Costo Ppto Ponderado Company', compute='_calc_cost_weighted_route', store=True)
    w_cost_impt_cpy = fields.Float(string='Costo Imputado Ponderado Company', compute='_calc_cost_weighted_route', store=True)
    w_cost_vigt_cpy = fields.Float(string='Costo Vigente Ponderado Company', compute='_calc_cost_weighted_route', store=True)
    prc_advance_impt = fields.Float(string='Porc Avance Imputación - No usar')
    w_cost_vigt_cpy_check_impt = fields.Float(string='Costo Vigente Imputado Ponderado Company', compute='_calc_cost_weighted_route', store=True)
    check_impt = fields.Boolean(String='Imputado', compute='_calc_cost_weighted_route', store=True)
    prc_avance_impt = fields.Float(string='Porc Avance Imputado', compute='_calc_cost_weighted_route', store=True)

    @api.depends('travel_route_id', 'travel_route_id.cost_ppto_cpy', 'travel_route_id.cost_impt_cpy', 'travel_route_id.cost_vigt_cpy', 'sale_order_line_id.check_assigned')
    def _calc_cost_weighted_route(self):
        #Calculamos el costo ponderado del tramo en base a la Linea de Venta del Pedido
        if self.travel_route_id.id:
            #Buscamos los subtotales de SOL de esta tabla
            d_sol_subtotal = self.env['tms.travel.route.service'].search([('travel_route_id', '=', self.travel_route_id.id)])
            #Proceso 01
            v_sum_sol_subtotal = 0
            v_cant_reg = 0
            if d_sol_subtotal:
                for records in d_sol_subtotal:
                    #contamos la cantidad de registros
                    v_cant_reg = v_cant_reg + 1
                    #Obtenemos los subtotales de todos los SOL del tramo seleccionado
                    v_sum_sol_subtotal = v_sum_sol_subtotal + records.sol_amount_untaxed_cpy
            #Proceso 02
            if d_sol_subtotal:
                #_logger.info("Se proceso 02")
                for records2 in d_sol_subtotal:
                    #Si hay OS con subtotal cero pero hay detalle de OS
                    if v_sum_sol_subtotal == 0 and v_cant_reg != 0:
                        v_porc_sol_subtotal = round(( 100 / v_cant_reg ),2)
                    #Si hay OS con subtotal manyor a cero
                    else:
                        if v_sum_sol_subtotal == 0:
                            v_sum_sol_subtotal = 1
                        v_porc_sol_subtotal = round(((records2.sol_amount_untaxed_cpy * 100) / v_sum_sol_subtotal ),2)

                    v_w_cost_ppto_cpy = round(((self.travel_route_id.cost_ppto_cpy * v_porc_sol_subtotal ) / 100),2)
                    v_w_cost_impt_cpy = round(((self.travel_route_id.cost_impt_cpy * v_porc_sol_subtotal ) / 100),2)
                    v_w_cost_vigt_cpy = round(((self.travel_route_id.cost_vigt_cpy * v_porc_sol_subtotal ) / 100),2)
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
