# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    accredit_move_id = fields.Many2one("account.move", string="movimiento acreditado")
    is_accredit_move = fields.Boolean(string="es un movimiento acreditado")
