# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class Report5thCategoryRent(models.AbstractModel):
    _name = 'report.cabalcon_hr_payroll.report_5th_category_rent'
    _description = 'Modelo de renta de 5ta categoría'

    @api.model
    def _get_report_values(self, docids, data=None):

        employees = self.env['hr.employee'].browse(self.env.context.get('active_ids'))
        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'data': data,

        }
