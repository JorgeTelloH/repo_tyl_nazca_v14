# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_pe_edi_endpoint_nubefact = fields.Char(string="EndPoint NubeFact", related="company_id.l10n_pe_edi_endpoint", readonly=False, help="EndPoint")
    l10n_pe_edi_token = fields.Char(string="Token", related="company_id.l10n_pe_edi_token", readonly=False)

