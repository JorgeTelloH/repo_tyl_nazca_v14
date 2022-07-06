# -*- coding:utf-8 -*-

from odoo import api, fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    contract_type_id = fields.Many2one('hr.contract.type', 'Contract Type')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    contract_type_id = fields.Many2one('hr.contract.type', 'Tipo de contrato')

    @api.onchange('contract_type_id')
    def onchange_contract_type_id(self):
        if self.contract_type_id:
            self.employee_id = False


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange('structure_id')
    def onchange_structure_id(self):
        if self.structure_id:
            domain = [('contract_id.structure_type_id.struct_ids', 'in', self.structure_id.id)]
            return {'domain': {'employee_ids': domain},}



