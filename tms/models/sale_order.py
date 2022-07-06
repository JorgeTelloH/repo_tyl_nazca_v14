# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"



    @api.depends('order_line.cost_ppto_cpy', 'order_line.cost_impt_cpy', 'order_line.cost_vigt_cpy', 'order_line')
    def _amount_all_costos(self):
        """
        Obtener el costo Operacional, Imputado y Vigente del Tramo del Viaje
        """
        for order_costos in self:
            amount_cost_ppto_cpy = 0.0
            amount_cost_impt_cpy = 0.0
            amount_cost_vigt_cpy = 0.0
            v_monto_vig_cpy_check_impt = 0.0
            v_cuenta_reg = 0
            v_cuenta_impt = 0
            v_check_impt = False
            for line in order_costos.order_line:
                amount_cost_ppto_cpy += line.cost_ppto_cpy
                amount_cost_impt_cpy += line.cost_impt_cpy
                amount_cost_vigt_cpy += line.cost_vigt_cpy
                if line.is_travel == True:
                    v_cuenta_reg = v_cuenta_reg + 1
                    v_monto_vig_cpy_check_impt = v_monto_vig_cpy_check_impt + line.cost_vigt_cpy_check_impt
                    if line.check_impt == True:
                        v_cuenta_impt = v_cuenta_impt + 1
            if v_cuenta_reg > 0:
                if v_cuenta_reg == v_cuenta_impt:
                    v_check_impt = True
            order_costos.update({
                'cst_ppto_operation_cpy': amount_cost_ppto_cpy,
                'cst_impt_cpy': amount_cost_impt_cpy,
                'cst_vigt_cpy': amount_cost_vigt_cpy,
                'check_impt': v_check_impt,
                'cost_vigt_cpy_check_impt': v_monto_vig_cpy_check_impt,
            })


    @api.depends('order_line.cst_ppto_expected')
    def _amount_ppto_expected(self):
        """
        Obtener el monto total de Costos Pptos de Comercial
        """
        for order1 in self:
            v_flete = 0.0
            v_carga = 0.0
            v_descarga = 0.0
            v_resguardo = 0.0
            v_otros = 0.0
            v_cst_esperado = 0.0
            v_cst_esperado_cpy = 0.0

            for line in order1.order_line:
                v_flete += line.cst_ppto_flete
                v_carga += line.cst_ppto_carga
                v_descarga += line.cst_ppto_descarga
                v_resguardo += line.cst_ppto_resguardo
                v_otros += line.cst_ppto_otros
                v_cst_esperado += line.cst_ppto_expected
                v_cst_esperado_cpy += line.cst_ppto_expected_cpy

            order1.update({
                'cst_ppto_flete': v_flete,
                'cst_ppto_carga': v_carga,
                'cst_ppto_descarga': v_descarga,
                'cst_ppto_resguardo': v_resguardo,
                'cst_ppto_otros': v_otros,
                'cst_ppto_expected': v_cst_esperado,
                'cst_ppto_expected_cpy': v_cst_esperado_cpy,
            })

    company_currency_amount = fields.Float(string='Total Company', compute='_find_amount_company', store=True)
    company_currency_amount_untaxed = fields.Float(string='Subtotal Company', compute='_find_amount_untaxed_company', store=True)
    cst_ppto_flete = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Flete')
    cst_ppto_carga = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Carga')
    cst_ppto_descarga = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Descarga')
    cst_ppto_resguardo = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Resguardo')
    cst_ppto_otros = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Otros')
    #Costo esperado = costo flete + carga + descarga + resguardo + otros
    cst_ppto_expected = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Esperado')
    cst_ppto_expected_cpy = fields.Float(compute ='_amount_ppto_expected', store=True, readonly=True, string='Costo Esperado Company')
    expected_margin = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Margen Esperado')
    expected_margin_cpy = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Margen Esperado Company')
    prc_expected_margin = fields.Float(compute='_compute_expected_margin', store=True, readonly=True, string='Porc Margen Esperado')
    #Costo Operacional --> se pobla desde Operaciones
    cst_ppto_operation = fields.Float(string='Costo Operacional', compute='_amount_operacional', store=True)
    cst_ppto_operation_cpy = fields.Float(string='Costo Operacional Company', compute='_amount_all_costos', store=True)
    operation_margin = fields.Float(string='Margen Operacional', compute='_amount_operacional', store=True)
    operation_margin_cpy = fields.Float(string='Margen Operacional Company', compute='_amount_operacional', store=True)
    prc_operation_margin_cpy = fields.Float(string='Porc Margen Operacional', compute='_amount_operacional', store=True)
    #Costo Real --> se pobla desde Operaciones
    cst_real = fields.Float(string='Costo Real - No Usar')
    cst_real_cpy = fields.Float(string='Costo Real Company - No Usar')
    real_margin = fields.Float(string='Margen Real - No Usar')
    real_margin_cpy = fields.Float(string='Margen Real Company - No Usar')
    prc_real_margin_cpy = fields.Float(string='Porc Margen Real - No Usar')
    prc_advance_impt = fields.Float(string='Porc Avance Imputación - No Usar')

    cst_vigt = fields.Float(string='Costo Vigente', compute='_amount_vigente', store=True)
    cst_vigt_cpy = fields.Float(string='Costo Vigente Company', compute='_amount_all_costos', store=True)
    vigt_margin = fields.Float(string='Margen Vigente', compute='_amount_vigente', store=True)
    vigt_margin_cpy = fields.Float(string='Margen Vigente Company', compute='_amount_vigente', store=True)
    prc_vigt_margin = fields.Float(string='Porc Margen Vigente', compute='_amount_vigente', store=True)

    cst_impt = fields.Float(string='Costo Imputado', compute='_amount_imputado', store=True)
    cst_impt_cpy = fields.Float(string='Costo Imputado Company', compute='_amount_all_costos', store=True)
    check_impt = fields.Boolean(string='Imputado', compute='_amount_all_costos', store=True)
    cost_vigt_cpy_check_impt = fields.Float(string='Costo Vigente Company Imputado', compute='_amount_all_costos', store=True)
    prc_avance_impt = fields.Float(string='Porc Avance Imputado', compute='_find_prc_avance_impt', store=True)

    cst_actual = fields.Float(string='Costo Actual', compute='_amount_actual', store=True)
    cst_actual_cpy = fields.Float(string='Costo Actual Company', compute='_amount_actual', store=True)
    actual_margin = fields.Float(string='Margen Actual', compute='_amount_actual', store=True)
    actual_margin_cpy = fields.Float(string='Margen Actual Company', compute='_amount_actual', store=True)
    prc_actual_margin = fields.Float(string='Porc Margen Actual', compute='_amount_actual', store=True)

    operation_count = fields.Integer(string='Conteo Operaciones', compute='_compute_count_operation')

    #Obtener el Costo Actual :: Si Vigt=0 then actual = esperado else actual = vigt
    @api.depends('cst_vigt_cpy','cst_ppto_expected_cpy')
    def _amount_actual(self):
        for order in self:

            if order.cst_vigt_cpy == 0:
                v_cst_actual_cpy = order.cst_ppto_expected_cpy
                v_cst_actual = order.cst_ppto_expected
            else:
                v_cst_actual_cpy = order.cst_vigt_cpy
                v_cst_actual = order.cst_vigt

            v_actual_margin = order.amount_untaxed - v_cst_actual
            v_actual_margin_cpy = order.company_currency_amount_untaxed - v_cst_actual_cpy

            if order.amount_untaxed == 0.0:
                v_subtotal = 1
            else:
                v_subtotal = order.amount_untaxed
            v_prc_actual_margin = round(((v_actual_margin * 100) / v_subtotal),2)

            order.cst_actual_cpy = v_cst_actual_cpy
            order.cst_actual = v_cst_actual
            order.actual_margin = v_actual_margin
            order.actual_margin_cpy = v_actual_margin_cpy
            order.prc_actual_margin = v_prc_actual_margin

    #Obtener Porcentaje de Avance Imputado
    @api.depends('cost_vigt_cpy_check_impt')
    def _find_prc_avance_impt(self):
        for order in self:
            v_avance_impt = 0
            if order.cst_vigt_cpy != 0:
                v_avance_impt = ((order.cost_vigt_cpy_check_impt * 100) / order.cst_vigt_cpy)
            order.prc_avance_impt = v_avance_impt

    #Obtener el Costo Operacional
    @api.depends('cst_ppto_operation_cpy', 'amount_untaxed', 'currency_id')
    def _amount_operacional(self):
        for so1 in self:
            if so1.currency_id == so1.company_id.currency_id:
                v_cst_ppto_operation = so1.cst_ppto_operation_cpy
            else:
                #pasar costo operacion a moneda extranjera
                # v_cst_ppto_operation = self.env['res.currency']._compute(so1.company_id.currency_id, so1.currency_id, so1.cst_ppto_operation_cpy)
                v_cst_ppto_operation = so1.company_id.currency_id.convert(so1.cst_ppto_operation_cpy,so1.currency_id,so1.company_id,fields.Date.today())



            v_operation_margin = so1.amount_untaxed - v_cst_ppto_operation
            v_operation_margin_cpy = so1.company_currency_amount_untaxed - so1.cst_ppto_operation_cpy
            if so1.company_currency_amount_untaxed == 0.0:
                v_subtotal = 1
            else:
                v_subtotal = so1.company_currency_amount_untaxed
            v_prc_operation_margin_cpy = round(((v_operation_margin_cpy * 100) / v_subtotal),2)

            so1.cst_ppto_operation = v_cst_ppto_operation
            so1.operation_margin = v_operation_margin
            so1.operation_margin_cpy = v_operation_margin_cpy
            so1.prc_operation_margin_cpy = v_prc_operation_margin_cpy

    #Obtener el Costo Imputado
    @api.depends('cst_impt_cpy', 'amount_untaxed', 'currency_id')
    def _amount_imputado(self):
        for so2 in self:
            if so2.currency_id == so2.company_id.currency_id:
                v_cst_impt = so2.cst_impt_cpy
            else:
                #pasar costo imputado a moneda extranjera
                #v_cst_impt = self.env['res.currency']._compute(so2.company_id.currency_id, so2.currency_id, so2.cst_impt_cpy)
                v_cst_impt = so2.company_id.currency_id.convert(so2.cst_impt_cpy, so2.currency_id,
                                                                  so2.company_id, fields.Date.today())

            so2.cst_impt = v_cst_impt

    #Obtener el Costo Vigente
    @api.depends('cst_vigt_cpy', 'amount_untaxed', 'currency_id')
    def _amount_vigente(self):
        for so3 in self:
            if so3.currency_id == so3.company_id.currency_id:
                v_cst_vigt = so3.cst_vigt_cpy
            else:
                #pasar costo vigente a moneda extranjera
                #v_cst_vigt = self.env['res.currency']._compute(so3.company_id.currency_id, so3.currency_id, so3.cst_vigt_cpy)
                v_cst_vigt = so3.company_id.currency_id.convert(so3.cst_vigt_cpy, so3.currency_id,
                                                        so3.company_id, fields.Date.today())

            v_vigt_margin = so3.amount_untaxed - v_cst_vigt
            v_vigt_margin_cpy = so3.company_currency_amount_untaxed - so3.cst_vigt_cpy
            if so3.amount_untaxed == 0.0:
                v_subtotal = 1
            else:
                v_subtotal = so3.amount_untaxed
            v_prc_vigt_margin = round(((v_vigt_margin * 100) / v_subtotal),2)

            so3.cst_vigt = v_cst_vigt
            so3.vigt_margin = v_vigt_margin
            so3.vigt_margin_cpy = v_vigt_margin_cpy
            so3.prc_vigt_margin = v_prc_vigt_margin


    def _compute_count_operation(self):
        self.operation_count = self.env['tms.route.operation'].search_count([('service_id', '=', self.name),('state','!=','canceled')])

    def action_view_count_operation(self):
        oper_obj = self.env['tms.route.operation'].search([('service_id', '=', self.name),('state','!=','canceled')])
        oper_ids = []
        for each in oper_obj:
            oper_ids.append(each.id)
        view_id = self.env.ref('tms.open_view_tms_route_operation_form').id

        if oper_ids:
            if len(oper_ids) <= 0:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'tms.route.operation',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': 'Operaciones',
                    'res_id': oper_ids and oper_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', oper_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'tms.route.operation',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': 'Operaciones',
                    'res_id': oper_ids
                }

            return value

    #Obtener el Margen Esperado (Venta sin impuestos - Costo Esperado)
    @api.depends('cst_ppto_expected', 'amount_untaxed')
    def _compute_expected_margin(self):
        for ol in self:
            v_expected_margin = ol.amount_untaxed - ol.cst_ppto_expected

            if ol.amount_untaxed == 0.0:
                v_subtotal = 1
            else:
                v_subtotal = ol.amount_untaxed

            ol.prc_expected_margin = round(((v_expected_margin * 100) / v_subtotal),2)
            ol.expected_margin = v_expected_margin

            if ol.currency_id == ol.company_id.currency_id:
                v_expected_margin_cpy = v_expected_margin
            else:
                if v_expected_margin != 0:
                    #v_expected_margin_cpy = self.env['res.currency']._compute(ol.currency_id, ol.company_id.currency_id, v_expected_margin)
                    v_expected_margin_cpy = ol.currency_id.convert(v_expected_margin, ol.company_id.currency_id,
                                                            ol.company_id, fields.Date.today())
                else:
                    v_expected_margin_cpy = 0

            ol.expected_margin_cpy = v_expected_margin_cpy

    @api.depends('amount_total', 'state')
    def _find_amount_company(self):
        for order in self:
            if order.currency_id == order.company_id.currency_id:
                price = order.amount_total
            else:
                if order.amount_total != 0:
                    #price = self.env['res.currency']._compute(order.currency_id, order.company_id.currency_id, order.amount_total)
                    price = order.currency_id.convert(order.amount_total, order.company_id.currency_id,
                                                                   order.company_id, fields.Date.today())
                else:
                    price = 0
            order.company_currency_amount = price

    @api.depends('amount_untaxed', 'state')
    def _find_amount_untaxed_company(self):
        for order in self:
            if order.currency_id == order.company_id.currency_id:
                price_untaxed = order.amount_untaxed
            else:
                if order.amount_untaxed != 0:
                    #price_untaxed = self.env['res.currency']._compute(order.currency_id, order.company_id.currency_id, order.amount_untaxed)
                    price_untaxed = order.currency_id.convert(order.amount_untaxed, order.company_id.currency_id,
                                                      order.company_id, fields.Date.today())
                else:
                    price_untaxed = 0
            order.company_currency_amount_untaxed = price_untaxed