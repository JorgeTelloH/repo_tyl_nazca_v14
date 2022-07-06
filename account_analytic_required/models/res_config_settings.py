# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_analytic_select = fields.Selection(
    	string="Analítica requerido", related='company_id.account_analytic_select', readonly= False)