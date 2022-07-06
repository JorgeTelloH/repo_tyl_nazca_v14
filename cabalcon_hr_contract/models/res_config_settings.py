# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_cabalcon_hr_contract_sequence = fields.Boolean(string="Autogenerar el código del contrato")
