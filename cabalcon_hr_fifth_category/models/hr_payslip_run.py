# -*- coding:utf-8 -*-

from datetime import date, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_close(self):
        _date = fields.Date.to_string(date.today().replace(day=1, month=1))
        struct_id = self.slip_ids.mapped('struct_id').id
        fifth = self.env['hr.fifth.category'].search([('date_from', '>=', _date), ('struct_id', '=', struct_id)], limit=1, order='date_from DESC')
        if fifth:
            fifth.state_paid()
        return super(HrPayslipRun, self).action_close()