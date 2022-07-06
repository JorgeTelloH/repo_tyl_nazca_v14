# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    move_line_dc = fields.Many2one('account.move.line', string='Asiento Diferencia de Cambio a conciliar', copy=False)