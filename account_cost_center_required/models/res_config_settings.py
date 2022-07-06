# -*- coding: utf-8 -*-
from odoo import models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_cost_center_select = fields.Selection(
    	string="Centro de Costo requerido", related='company_id.account_cost_center_select', readonly= False)