# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    target_debit_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe')
    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')