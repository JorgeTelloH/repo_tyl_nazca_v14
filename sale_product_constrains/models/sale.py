# -*- coding: utf-8 -*-
from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    _sql_constraints = [
        ('ref_partner_uniq', 'UNIQUE (client_order_ref, partner_id)', 'Referencia del Cliente debe ser unico!'),
    ]