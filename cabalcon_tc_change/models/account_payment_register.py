# -*- encoding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    exchange_rate_value_p = fields.Float(string='Tipo de Cambio', digits=dp.get_precision('Tipo Cambio'))

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()

        exchange_value = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), 
                                                               ('name', '=', self.payment_date)])
        for payment in payments:
            if exchange_value:
                self.exchange_rate_value_p = 1/(exchange_value.rate)
                payment.exchange_rate_value = 1/(exchange_value.rate)
            else:
                exchange_value = self.env['res.currency.rate'].search([('currency_id', '=', self.currency_id.id), 
                                                                       ('name', '<=', self.payment_date)], order='name desc', limit=1)
                self.exchange_rate_value_p = 1/(exchange_value.rate) if exchange_value else 1.000
                payment.exchange_rate_value = 1/(exchange_value.rate) if exchange_value else 1.000

        return payments