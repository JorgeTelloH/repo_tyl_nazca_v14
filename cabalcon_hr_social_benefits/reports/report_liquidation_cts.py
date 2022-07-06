# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class LiquidationCTSReport(models.AbstractModel):
    _name = 'report.cabalcon_hr_social_benefits.report_liquidation_cts'
    _description = 'Modelo de liquidación de depósitos semestrales de CTS'

    @api.model
    def _get_report_values(self, docids, data=None):

        employees = self.env['hr.social.benefits.gratification'].browse(docids)

        if all(emp.benefit_type in ['liquidation', 'gratification'] for emp in employees):
            raise UserError("Este reporte debe ser invocado desde la vista CTS")

        return {
            'doc_ids': docids,
            'doc_model': 'hr.social.benefits.gratification',
            'docs': employees,
            'data': data,

        }
