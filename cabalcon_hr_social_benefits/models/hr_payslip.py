from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    def action_import_social_benefits(self):
        domain = [('state', '=', 'close'), ('report_date', '>=', self.date_from), ('report_date', '<=', self.date_to)]
        domain_gr = domain + [('benefit_type', '=', 'gratification')]
        social_benefits_gr = self.env['hr.social.benefits'].sudo().search(domain_gr)
        domain_cts = domain + [('benefit_type', '=', 'ctc')]
        social_benefits_cts = self.env['hr.social.benefits'].sudo().search(domain_cts)
        domain_liquidation = domain + [('benefit_type', '=', 'liquidation')]
        social_benefits_liquidations = self.env['hr.social.benefits'].sudo().search(domain_liquidation)

        input_type_gr = self.env['hr.payslip.input.type'].search([('code', '=', 'GR')], limit=1)
        if not input_type_gr:
            raise ValidationError('No se encontro la entrada con código GR, verifique en el menú Configuración > Otros tipo entradas si existe')
        input_type_bonus = self.env['hr.payslip.input.type'].search([('code', '=', 'BSBONO')], limit=1)
        if not input_type_bonus:
            raise ValidationError('No se encontro la entrada con código BSBONO, verifique en el menú Configuración > Otros tipo entradas si existe')
        social_benefit = social_benefits_gr.gratification_ids.filtered(lambda sb: sb.employee_id == self.employee_id and sb.contract_id == self.contract_id)
        input_line_ids = []
        if social_benefit:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_gr.id)
            if line:
                line.write({'amount': social_benefit.amount_gratification})
            else:
                item = [0, 0, {'input_type_id': input_type_gr.id, 'amount': social_benefit.amount_gratification}]
                input_line_ids.append(item)

            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_bonus.id)
            if line:
                line.write({'amount': social_benefit.amount_bonus})
            else:
                item = [0, 0, {'input_type_id': input_type_bonus.id, 'amount': social_benefit.amount_bonus}]
                input_line_ids.append(item)
            if input_line_ids:
                self.input_line_ids = input_line_ids

        # LIQUIDACION
        input_type_cts = self.env['hr.payslip.input.type'].search([('code', '=', 'CTS')], limit=1)
        if not input_type_cts:
            raise ValidationError('No se encontro la entrada con código CTS, verifique en el menú Configuración > Otros tipo entradas si existe')
        social_benefit = social_benefits_cts.gratification_ids.filtered(lambda sb: sb.employee_id == self.employee_id and sb.contract_id == self.contract_id)
        input_line_ids = []
        if social_benefit:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_cts.id)
            if line:
                line.write({'amount': social_benefit.amount_cts})
            else:
                item = [0, 0, {'input_type_id': input_type_cts.id, 'amount': social_benefit.amount_cts}]
                input_line_ids.append(item)
                self.input_line_ids = input_line_ids

        input_type_gr = self.env['hr.payslip.input.type'].search([('code', '=', 'GRTRUNCA')], limit=1)
        if not input_type_gr:
            raise ValidationError('No se encontro la entrada con código GRTRUNCA, verifique en el menú Configuración > Otros tipo entradas si existe')
        social_benefit = social_benefits_liquidations.gratification_trunca_ids.filtered(lambda sb: sb.employee_id == self.employee_id and sb.contract_id == self.contract_id)
        input_line_ids = []
        if social_benefit:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_gr.id)
            if line:
                line.write({'amount': social_benefit.amount_total})
            else:
                item = [0, 0, {'input_type_id': input_type_gr.id, 'amount': social_benefit.amount_total}]
                input_line_ids.append(item)
                self.input_line_ids = input_line_ids

        input_type_cts = self.env['hr.payslip.input.type'].search([('code', '=', 'CTSTRUNCA')], limit=1)
        if not input_type_cts:
            raise ValidationError('No se encontro la entrada con código CTSTRUNCA, verifique en el menú Configuración > Otros tipo entradas si existe')
        social_benefit = social_benefits_liquidations.cts_trunca_ids.filtered(lambda sb: sb.employee_id == self.employee_id and sb.contract_id == self.contract_id)
        input_line_ids = []
        if social_benefit:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_cts.id)
            if line:
                line.write({'amount': social_benefit.amount_cts})
            else:
                item = [0, 0, {'input_type_id': input_type_cts.id, 'amount': social_benefit.amount_cts}]
                input_line_ids.append(item)
                self.input_line_ids = input_line_ids

        # LIQUIDACION (Vacaciones)
        input_type_vac = self.env['hr.payslip.input.type'].search([('code', '=', 'VACLIQ')], limit=1)
        if not input_type_vac:
            raise ValidationError('No se encontro la entrada con código VACLIQ, verifique en el menú Configuración > Otros tipo entradas si existe')
        input_type_vac_trun = self.env['hr.payslip.input.type'].search([('code', '=', 'VACTRUN')], limit=1)
        if not input_type_vac_trun:
            raise ValidationError('No se encontro la entrada con código VACTRUN, verifique en el menú Configuración > Otros tipo entradas si existe')
        social_benefit = social_benefits_liquidations.vacation_ids.filtered(lambda sb: sb.employee_id == self.employee_id and sb.contract_id == self.contract_id)
        input_line_ids = []
        if social_benefit and social_benefit.days_vacation > 0:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_vac.id)
            if line:
                line.write({'amount': social_benefit.amount_vacation})
            else:
                item = [0, 0, {'input_type_id': input_type_vac.id, 'amount': social_benefit.amount_vacation}]
                input_line_ids.append(item)

        if social_benefit and social_benefit.amount_vacation_trunca > 0:
            line = self.input_line_ids.filtered(lambda ls: ls.input_type_id.id == input_type_vac_trun.id)
            if line:
                line.write({'amount': social_benefit.amount_vacation_trunca})
            else:
                item = [0, 0, {'input_type_id': input_type_vac_trun.id, 'amount': social_benefit.amount_vacation_trunca}]
                input_line_ids.append(item)

        if input_line_ids:
            self.input_line_ids = input_line_ids

        self.compute_sheet()
