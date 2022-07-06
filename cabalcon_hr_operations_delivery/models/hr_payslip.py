from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, contract_ids, date_from, date_to):
        # res = self.input_line_ids
        res = super(PayslipOverTime, self).get_inputs(contract_ids, date_from, date_to)
        contract = self.env['hr.contract'].browse(contract_ids.id)
        emp_id = contract.employee_id
        overtimes = self.env['calendar.operation'].search([('employee_id', '=', emp_id.id),
                                                       ('date', '>=', date_from),
                                                       ('date', '<=', date_to),
                                                       ('approve', '=', True)])
        hours_extra_25 = 0
        hours_extra_35 = 0
        production = 0
        if contract.structure_type_id.wage_type == 'hourly':
            wage_day = contract.wage
        else:
            wage_day = contract.wage/30/8

        for ovt in overtimes:
            hours_extra_25 += ovt.hours_extra_25
            hours_extra_35 += ovt.hours_extra_35
            production += ovt.total_production

        result = res.filtered(lambda a: a.code == 'OVERTIME25')
        amount25 = round(hours_extra_25 * (wage_day + wage_day * 0.25), 2)
        amount35 = round(hours_extra_35 * (wage_day + wage_day * 0.35), 2)
        if result:
            result['amount'] = amount25
        elif amount25 > 0:
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'OVERTIME25')], limit=1)
            values = {'input_type_id': input_type.id, 'amount': amount25}
            res += result.new(values)

        result = res.filtered(lambda a: a.code == 'OVERTIME35')
        if result:
            result['amount'] = amount35
        elif amount35 > 0:
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'OVERTIME35')], limit=1)
            values = {'input_type_id': input_type.id, 'amount': amount35}
            res += result.new(values)

        result = res.filtered(lambda a: a.code == 'PRODUCTION')
        if result:
            result['amount'] = production
        elif production > 0:
            input_type = self.env['hr.payslip.input.type'].search([('code', '=', 'PRODUCTION')], limit=1)
            values = {'input_type_id': input_type.id, 'amount': production}
            res += result.new(values)

        return res
