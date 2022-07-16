# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    currency_tc = fields.Float(string='Tipo de Cambio', digits='Tipo Cambio')

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()

        v_rate_pe = 1
        if self.currency_id != self.company_currency_id:
            excha = self.env['res.currency.rate'].search([
                ('currency_id', '=', self.currency_id.id), ('name', '=', self.payment_date), ('company_id','=', self.company_id.id)
                ], limit=1)
            if excha:
                v_rate_pe = excha.rate_pe
            else:
                excha = self.env['res.currency.rate'].search([
                    ('currency_id', '=', self.currency_id.id), ('name', '<=', self.payment_date), ('company_id','=', self.company_id.id)
                    ], order='name desc', limit=1)
                v_rate_pe = excha.rate_pe if excha else 1

        for payment in payments:
            self.currency_tc = v_rate_pe
            payment.currency_tc = v_rate_pe

        return payments