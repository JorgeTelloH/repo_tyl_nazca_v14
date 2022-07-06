# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_amount_to_text(self, value):
        currency = self.company_id.currency_id
        return currency.amount_to_text(value)

