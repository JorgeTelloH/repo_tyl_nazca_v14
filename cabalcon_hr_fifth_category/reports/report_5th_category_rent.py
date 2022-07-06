# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class Report5thCategoryRent(models.AbstractModel):
    _name = 'report.cabalcon_hr_fifth_category.report_5th_category_rent'
    _description = 'Modelo de renta de 5ta categoría'

    @api.model
    def _get_report_values(self, docids, data=None):

        employees = self.env['hr.fifth.category.lines'].browse(docids)  # self.env.context.get('active_ids')
        return {
            'doc_ids': docids,
            'doc_model': 'hr.fifth.category.lines',
            'docs': employees,
            'data': data,

        }
