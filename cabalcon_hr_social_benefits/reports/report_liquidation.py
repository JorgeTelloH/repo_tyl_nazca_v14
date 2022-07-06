# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class LiquidationReport(models.AbstractModel):
    _name = 'report.cabalcon_hr_social_benefits.report_liquidation'
    _description = 'Modelo de liquidación por tiempo de servicios'

    @api.model
    def _get_report_values(self, docids, data=None):
        social_benefit = data['social_benefit_id'][0]
        benefits = self.env['hr.social.benefits'].browse(social_benefit)
        if data['employee_ids']:
            docids = data['employee_ids']
        else:
            docids = benefits.get_employees_ids()

        employees = self.env['hr.employee'].browse(docids)

        report_data = {}

        for emp in employees:
            gratification = benefits.gratification_trunca_ids.filtered(lambda g: g.employee_id.id == emp.id)
            cts = benefits.cts_trunca_ids.filtered(lambda g: g.employee_id.id == emp.id)
            vacation = benefits.vacation_ids.filtered(lambda g: g.employee_id.id == emp.id)
            values = {'departure_date': gratification.contract_id.date_end.strftime('%d/%m/%Y'),
                      'wage': gratification.wage,
                      'da': gratification.da,
                      'overtime': gratification.overtime,
                      'computable_remuneration': gratification.computable_remuneration,
                      'amount_gratification1_6to': cts.amount_gratification1_6to,
                      'cts_liquidation_date_init': '',
                      'cts_name': 'CTS',
                      'months_work': cts.months_work,
                      'days_work': cts.days_work,
                      'vac_months_work': vacation.months_work,
                      'vac_days_work': vacation.days_work,
                      'days_vacation': vacation.days_vacation,
                      'gratification_description': '',
                      'amount_bonus': gratification.amount_bonus,
                      'grat_months_work': gratification.months_work,
                      'grat_days_work': gratification.days_work,
                      }

            report_data[emp.id] = values

        return {
            'doc_ids': docids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'report_data': report_data,

        }
