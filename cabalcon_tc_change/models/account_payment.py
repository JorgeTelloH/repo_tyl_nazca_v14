# -*- encoding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class AccountMove(models.Model):
    _inherit = 'account.payment'


    exchange_rate_value= fields.Float(string='Tipo de Cambio', digits=dp.get_precision('Tipo Cambio'))

    @api.onchange('date', 'currency_id', 'partner_id')
    def get_exchange_rate_value(self):
        excha = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), ('name', '=', self.date)])
        if excha:
            self.exchange_rate_value = 1/(excha.rate)
        elif self.currency_id:
            excha = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), ('name', '<=', self.date)], order='name desc', limit=1)
            self.exchange_rate_value = 1/(excha.rate) if excha else 1.000