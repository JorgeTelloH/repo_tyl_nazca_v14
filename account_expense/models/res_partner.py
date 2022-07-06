# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    property_account_expense_payable_id = fields.Many2one('account.account', company_dependent=True,
                                                  string="Cuenta por pagar de gastos",
                                                  domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
                                                  help="This account will be used instead of the default one as the payable account for the current partner")

    property_account_expense_receivable_id = fields.Many2one('account.account', company_dependent=True,
                                                     string="Cuenta por cobrar de gastos",
                                                     domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
                                                     help="This account will be used instead of the default one as the receivable account for the current partner")