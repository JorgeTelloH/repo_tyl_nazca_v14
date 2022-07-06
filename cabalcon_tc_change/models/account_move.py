# -*- encoding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_special_tc = fields.Boolean(string='Activar Tipo Cambio', help='Activar el Tipo de Cambio personalizado por el usuario')
    currency_tc = fields.Float(string='Tipo de Cambio', digits=dp.get_precision('Tipo Cambio'))

    @api.onchange('is_special_tc','currency_id')
    def onchange_is_special_tc(self):        
        for rec in self:
            if not rec.is_special_tc:
                rec.currency_tc = (1/rec.currency_id.rate)
                for line in rec.line_ids:
                    line._onchange_amount_currency()

    @api.onchange('currency_tc')
    def onchange_currency_tc(self):
        for rec in self:
            for line in rec.line_ids:
                line._onchange_amount_currency()

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        for rec in self:
            for line in rec.line_ids:
                line._onchange_amount_currency()

    @api.constrains('is_special_tc')
    def contrains_not_zero(self):
        if self.is_special_tc:
            if self.currency_tc <= 0.00:
                raise ValidationError(_('El tipo de Cambio no puede ser menor o igual que 0'))

    def _reverse_moves(self, default_values_list=None, cancel=False):
        reverse_moves = super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        reverse_moves.onchange_currency_tc()
        return reverse_moves


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    exchange_rate_value= fields.Float(related='move_id.currency_tc', string='Tipo de Cambio', digits=dp.get_precision('Tipo Cambio'))

    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            company = line.move_id.company_id
            if line.move_id.is_special_tc and line.move_id.currency_tc > 0:
                balance = line.currency_id.with_context(default_pen_rate=self.move_id.currency_tc)._convert(
                    line.amount_currency, company.currency_id, company,
                    line.move_id.date or fields.Date.context_today(line))
            else:
                balance = line.currency_id._convert(line.amount_currency, company.currency_id, company,
                                                    line.move_id.date or fields.Date.context_today(line))
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())
