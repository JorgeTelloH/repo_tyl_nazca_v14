# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    social_benefits_gratification_id = fields.Many2one('hr.social.benefits', string='Gratificación')
    social_benefits_cts_id = fields.Many2one('hr.social.benefits', string='CTS')
    social_benefits_liquidation_id = fields.Many2one('hr.social.benefits', string='Liquidación')

    def action_import_social_benefits(self):
        domain = [('state', '=', 'close'), ('report_date', '>=', self.date_start), ('report_date', '<=', self.date_end)]
        domain_gr = domain + [('benefit_type', '=', 'gratification')]
        social_benefits_gr = self.env['hr.social.benefits'].sudo().search(domain_gr, limit=1)
        domain_cts = domain + [('benefit_type', '=', 'cts')]
        social_benefits_cts = self.env['hr.social.benefits'].sudo().search(domain_cts, limit=1)
        domain_liquidation = domain + [('benefit_type', '=', 'liquidation')]
        social_benefits_liquidations = self.env['hr.social.benefits'].sudo().search(domain_liquidation, limit=1)

        payslip_ids = []
        input_type_gr = self.env['hr.payslip.input.type'].search([('code', '=', 'GR')], limit=1)
        input_type_bonus = self.env['hr.payslip.input.type'].search([('code', '=', 'BSBONO')], limit=1)
        for sb in social_benefits_gr.gratification_ids:
            input_line_ids = []
            payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == sb.employee_id and ps.contract_id == sb.contract_id)
            if payslip:
                line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_gr.id)
                if line:
                    line.write({'amount': sb.amount_gratification})
                else:
                    item = [0, 0, {'input_type_id': input_type_gr.id, 'amount': sb.amount_gratification}]
                    input_line_ids.append(item)
                line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_bonus.id)
                if line:
                    line.write({'amount': sb.amount_bonus})
                else:
                    item = [0, 0, {'input_type_id': input_type_bonus.id, 'amount': sb.amount_bonus}]
                    input_line_ids.append(item)
                    payslip.input_line_ids = input_line_ids
                    payslip_ids.append(payslip.id)

        input_type_cts = self.env['hr.payslip.input.type'].search([('code', '=', 'CTS')], limit=1)
        for sb in social_benefits_cts.gratification_ids:
            input_line_ids = []
            payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == sb.employee_id and ps.contract_id == sb.contract_id)
            if payslip:
                line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_cts.id)
                if line:
                    line.write({'amount': sb.amount_cts})
                else:
                    item = [0, 0, {'input_type_id': input_type_cts.id, 'amount': sb.amount_cts}]
                    input_line_ids.append(item)
                    payslip.input_line_ids = input_line_ids
                    payslip_ids.append(payslip.id)

        # LIQUIDACION
        input_type_gr = self.env['hr.payslip.input.type'].search([('code', '=', 'GRTRUNCA')], limit=1)
        for lq in social_benefits_liquidations.gratification_trunca_ids:
            payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == lq.employee_id and ps.contract_id == lq.contract_id)
            if payslip:
                line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_gr.id)
                if line:
                    line.write({'amount': sb.amount_total})
                else:
                    item = [0, 0, {'input_type_id': input_type_gr.id, 'amount': sb.amount_total}]
                    input_line_ids.append(item)
                    payslip.input_line_ids = input_line_ids
                    payslip_ids.append(payslip.id)

        input_type_cts = self.env['hr.payslip.input.type'].search([('code', '=', 'CTSTRUNCA')], limit=1)
        for lq in social_benefits_liquidations.cts_trunca_ids:
            input_line_ids = []
            payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == lq.employee_id and ps.contract_id == lq.contract_id)
            if payslip:
                line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_cts.id)
                if line:
                    line.write({'amount': sb.amount_cts})
                else:
                    item = [0, 0, {'input_type_id': input_type_cts.id, 'amount': sb.amount_cts}]
                    input_line_ids.append(item)
                    payslip.input_line_ids = input_line_ids
                    payslip_ids.append(payslip.id)

        input_type_vac = self.env['hr.payslip.input.type'].search([('code', '=', 'VACLIQ')], limit=1)
        input_type_vac_trun = self.env['hr.payslip.input.type'].search([('code', '=', 'VACTRUN')], limit=1)
        for vac in social_benefits_liquidations.vacation_ids:
            input_line_ids = []
            if vac.days_vacation > 0:
                payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == vac.employee_id and ps.contract_id == vac.contract_id)
                if payslip:
                    line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_vac.id)
                    if line:
                        line.write({'amount': sb.amount_vacation})
                    else:
                        item = [0, 0, {'input_type_id': input_type_vac.id, 'amount': sb.amount_vacation}]
                        input_line_ids.append(item)
                        payslip.input_line_ids = input_line_ids
                        payslip_ids.append(payslip.id)
            if vac.amount_vacation_trunca > 0:
                payslip = self.slip_ids.filtered(lambda ps: ps.employee_id == vac.employee_id and ps.contract_id == vac.contract_id)
                if payslip:
                    line = payslip.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_vac_trun.id)
                    if line:
                        line.write({'amount': sb.amount_vacation_trunca})
                    else:
                        item = [0, 0, {'input_type_id': input_type_vac_trun.id, 'amount': sb.amount_vacation_trunca}]
                        input_line_ids.append(item)
                        payslip.input_line_ids = input_line_ids
                        payslip_ids.append(payslip.id)

        self.write({'social_benefits_gratification_id': social_benefits_gr.id,
                    'social_benefits_cts_id': social_benefits_cts.id,
                    'social_benefits_liquidation_id': social_benefits_liquidations.id})

        ids = list(set(payslip_ids))
        for payslip in self.env['hr.payslip'].browse(ids):
            payslip.compute_sheet()

    def action_close(self):
        if self.social_benefits_gratification_id:
            self.env['hr.social.benefits'].sudo().browse(self.social_benefits_gratification_id.id).write({'state': 'paid'})
        if self.social_benefits_cts_id:
            self.env['hr.social.benefits'].sudo().browse(self.social_benefits_cts_id.id).write({'state': 'paid'})
        if self.social_benefits_liquidation_id:
            self.env['hr.social.benefits'].sudo().browse(self.social_benefits_liquidation_id.id).write({'state': 'paid'})

        super(HrPayslipRun, self).action_close()

