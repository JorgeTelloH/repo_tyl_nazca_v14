# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    expense_inv_id = fields.Many2one('account.expense', string='Gasto', domain=[('state', '=', 'approved')], copy=False,
                                 readonly=True, states={'draft': [('readonly', False)]})