# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
class ResCurrency(models.Model):
	_inherit = 'res.currency'

	code_ple = fields.Char(string="Codigo PLE impresion moneda")