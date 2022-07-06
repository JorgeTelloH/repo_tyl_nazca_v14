# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_expense_id = fields.Many2one('account.journal', string='Diario de Gasto', related='company_id.journal_expense_id', readonly=False)
    account_expense_reci = fields.Many2one('account.account', string='Cuenta por Cobrar Gasto', related='company_id.account_expense_reci', readonly=False)
    account_expense_pay = fields.Many2one('account.account', string='Cuenta por Pagar Gasto', related='company_id.account_expense_pay', readonly=False)