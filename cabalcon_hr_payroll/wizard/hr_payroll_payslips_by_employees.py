# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    # def get_structure_domain(self):
    #     if self.env.context.get('active_id'):
    #         payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
    #         date_from = payslip_run.date_start
    #         date_to = payslip_run.date_end
    #         domain = [('date_from', '>=', str(date_from)),
    #                   ('date_to', '<=', str(date_to)),
    #                   ('state', '=', 'done'),
    #                   ('refund', '=', False),
    #                   ('credit_note', '=', False)]
    #         payslips = self.env['hr.payslip'].search(domain)
    #         return [('id', 'not in', payslips.mapped('struct_id').ids)]
    #     else:
    #         return []
    #
    # structure_id = fields.Many2one('hr.payroll.structure', domain=get_structure_domain)

    @api.onchange('structure_id')
    def _onchange_structure_id(self):
        if self.structure_id:
            self.employee_ids = [(5, 0, 0)]
            domain = self._get_available_contracts_domain()
            if not self.env.context.get('active_id'):
                from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
                end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            else:
                payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
                from_date = payslip_run.date_start
                end_date = payslip_run.date_end
            if end_date:
                domain += [('contract_ids.date_start', '<', str(end_date))]

            if from_date and end_date:
                domain_slip = [('date_from', '>=', str(from_date)),
                               ('date_to', '<=', str(end_date)),
                               ('state', 'in', ['draft','verify', 'done']),
                               ('refund', '=', False),
                               ('credit_note', '=', False),
                               ('struct_id', '=', self.structure_id.id)]

                emp_in_payslips = self.env['hr.payslip'].search(domain_slip).mapped("employee_id").ids
                if len(emp_in_payslips) > 0:
                    domain += [('id', 'not in', emp_in_payslips)]

            if self.structure_id.contract_type_id:
                domain += [('contract_ids.contract_type_id', '=', self.structure_id.contract_type_id.id)]
            self.employee_ids = self.env['hr.employee'].search(domain)
        else:
            self.employee_ids = [(5, 0, 0)]

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        employees = self.with_context(active_test=False).employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'near_expire', 'close']
        ).filtered(lambda c: c.active)
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if (self.structure_id.type_id.default_struct_id == self.structure_id):
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            if work_entries._check_if_error():
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'sticky': False,
                    }
                }

        default_values = Payslip.default_get(Payslip.fields_get())
        payslip_values = [dict(default_values, **{
            'name': 'Payslip - %s' % (contract.employee_id.name),
            'employee_id': contract.employee_id.id,
            'credit_note': payslip_run.credit_note,
            'payslip_run_id': payslip_run.id,
            'date_from': payslip_run.date_start,
            'date_to': payslip_run.date_end,
            'contract_id': contract.id,
            'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            'contract_type_id': contract.contract_type_id.id
        }) for contract in contracts]

        payslips = Payslip.with_context(tracking_disable=True).create(payslip_values)
        for payslip in payslips:
            payslip._onchange_employee()

        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
