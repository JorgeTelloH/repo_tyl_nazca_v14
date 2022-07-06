# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    automatic_destiny = fields.Boolean(string='Destinos automaticos', related='company_id.automatic_destiny', readonly=False,)
    # priorise_destiny = fields.Selection([('analitic', "Cuenta analitica"), ('cost_center', "Centro de costo")],
    #                                     string='Priorizar destino', related='company_id.priorise_destiny')