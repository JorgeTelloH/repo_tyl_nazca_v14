# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.payment'

    currency_tc= fields.Float(string='Tipo de Cambio', digits='Tipo Cambio')

    @api.onchange('date', 'currency_id', 'partner_id')
    def get_currency_tc(self):
        v_rate_pe = 1
        if self.currency_id != self.company_id.currency_id:
            excha = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id), ('name', '=', self.date), ('company_id','=', self.company_id.id)
                ], limit=1)
            if excha:
                v_rate_pe = excha.rate_pe
            else:
                excha = self.env['res.currency.rate'].search([
                    ('currency_id', '=', self.currency_id.id), ('name', '<=', self.date), ('company_id','=', self.company_id.id)
                    ], order='name desc', limit=1)
                v_rate_pe = excha.rate_pe if excha else 1

        self.currency_tc = v_rate_pe
