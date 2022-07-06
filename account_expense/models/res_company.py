# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    journal_expense_id = fields.Many2one('account.journal', string='Diario de Gasto')
    account_expense_reci = fields.Many2one('account.account', string='Cuenta por cobrar Gasto')
    account_expense_pay = fields.Many2one('account.account', string='Cuenta por pagar Gasto')