# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    travel_allowance_month = fields.Boolean(string="Movilidad  Mensual", help="Subsidio de transporte Mensual o diario")
    travel_allowance = fields.Monetary(string="Movilidad Mensual", help="Subsidio de transporte")
    is_af = fields.Boolean(related='company_id.is_af')
    is_da = fields.Boolean(string='Tiene Asignación Familiar', compute="_compute_is_da", readonly=True)
    da = fields.Float(string="Asignación Familiar", compute="_compute_da", readonly=True, help="Asignación Familiar")
    meal_allowance = fields.Monetary(string="Subsidio de alimentación", help="Subsidio de alimentación")
    medical_allowance = fields.Monetary(string="Asignación médica", help="Asignación médica")
    produce_5ta_category = fields.Monetary(string='Renta 5ta Categoría')
    judicial_retention = fields.Monetary(string='Retención judicial')
    basket = fields.Monetary(string='Aguinaldo')
    is_voluntary_contribution = fields.Boolean(string='Aporte voluntario con fin previsional')
    voluntary_contribution = fields.Float(string='Importe')
    is_voluntary_endless_contribution = fields.Boolean(string='Aporte voluntario sin fin previsional')
    voluntary_endless_contribution = fields.Float(string='Importe')
    advance = fields.Float(string='Adelanto')


    def _compute_is_da(self):
        for contract in self:
            if contract.is_af:
                contract.is_da = (contract.employee_id.minor_children > 0) or contract.employee_id.is_university
            else:
                contract.is_da = False
        
    def _compute_da(self):
        for contract in self:
            if contract.is_af:
                contract.da = contract.company_id.essalud_rmv * (contract.company_id.percent_af/100)
            else:
                contract.da = 0



