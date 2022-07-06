# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    birth_date = fields.Date(string="Fecha Cumpleaños")
    anniversary_date = fields.Date(string="Fecha Aniversario")
