# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    has_eps = fields.Boolean(string='Incluye cálculo de EPS', default=False)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    # Campo para saber que Es una aportación del empleador y se utilizara en la boleta de pago
    is_employer_contributions = fields.Boolean(string='Es una aportación del empleador', default=False)
    
