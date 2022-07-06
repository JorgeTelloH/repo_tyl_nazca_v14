# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_advance_payment = fields.Boolean(string='Es un Adelanto?')
    advance_id = fields.Many2one('tms.advance', string = 'Adelanto', domain=[('state', '=', 'approved')])
