# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_provider = fields.Selection(selection_add=[('nubefact', 'NubeFact')])
    l10n_pe_edi_endpoint = fields.Char(string="EndPoint", help="EndPoint")
    l10n_pe_edi_token = fields.Char(string="Token")
