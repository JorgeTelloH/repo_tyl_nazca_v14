# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    move_by_employee = fields.Boolean(string='Asiento contable por empleado', default=True)
