# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields


# class HrPayslipInput(models.Model):
#     _inherit = 'hr.payslip.input'
#
#     participation_line_id = fields.Many2one('hr.employee.participation.line', string="Commission Line")


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    commission_ids = fields.One2many('hr.employee.participation.line', inverse_name='payslip_id', string='Commission')

    def get_inputs(self, contract_ids, date_from, date_to):

        res = super(Payslip, self).get_inputs(contract_ids, date_from, date_to)
        # res = self.input_line_ids
        # contract_obj = self.env['hr.contract']
        contract_id = contract_ids[0].id
        commissions = self.env['hr.employee.participation.line'].search([('state', '=', 'approved'),
                                                                         ('paid', '=', False),
                                                                         ('report_date', '>=', date_from),
                                                                         ('report_date', '<=', date_to),
                                                                         ('contract_id', '=', contract_id)])
        commission_amount = 0
        commission_ids = []
        for part_line in commissions:
            commission_ids.append(part_line.part_id.id)
            commission_amount += part_line.part_value

        self.commission_ids = [(6, 0, commission_ids)]

        if commission_amount > 0:
            result = res.filtered(lambda a: a.code == 'COMM')
            if result:
                result['amount'] = commission_amount
            else:
                input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'COMM')], limit=1)
                values = {'input_type_id': input_type.id, 'amount': commission_amount}
                res += result.new(values)

        return res

    def action_payslip_done(self):
        for slip in self:
            slip.commission_ids.write({'paid': True})

        return super(Payslip, self).action_payslip_done()
