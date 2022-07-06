# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    team_id = fields.Many2one(related="sale_id.team_id", string="Equipo de ventas", store=True, readonly=False)
    client_order_ref = fields.Char(related="sale_id.client_order_ref", string="Referencia del Cliente", store=True, readonly=False)
