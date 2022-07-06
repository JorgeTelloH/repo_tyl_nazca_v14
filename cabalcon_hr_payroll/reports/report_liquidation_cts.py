# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError

# TODO: ESTE REPORTE SE DEBE PASAR AL MODULO DE BENEFICIOS SOCIALES
class LiquidationCTSReport(models.AbstractModel):
    _name = 'report.cabalcon_hr_payroll.report_liquidation_cts'
    _description = 'Modelo de liquidación de depósitos semestrales de CTS'

    @api.model
    def _get_report_values(self, docids, data=None):

        employees = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'data': data,

        }
