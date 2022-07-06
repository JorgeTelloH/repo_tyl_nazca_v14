# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_purchase_id = fields.Many2one('res.currency', related="company_id.currency_purchase_id", string='Moneda de Compra')
    currency_sale_id = fields.Many2one('res.currency', related="company_id.currency_sale_id", string='Moneda de Venta')
    auto_currency_rate = fields.Boolean(string='Actualización automática', related="company_id.auto_currency_rate")
    currency_next_execution_date = fields.Date(string='Próxima Fecha de Ejecución', related="company_id.currency_next_execution_date")