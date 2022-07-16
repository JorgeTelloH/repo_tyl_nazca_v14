# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
#_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_special_tc = fields.Boolean(string='Activar Tipo Cambio', help='Activar el Tipo de Cambio personalizado por el usuario')
    currency_tc = fields.Float(string='Tipo de Cambio', digits='Tipo Cambio', default=1.0)
    is_invoice_in_me = fields.Boolean(string="Es Documento en Moneda Extranjera",compute="compute_is_invoice_in_me",store=True)
    invoice_date = fields.Date(default=fields.Date.context_today)


    @api.depends('company_id','currency_id')
    def compute_is_invoice_in_me(self):
        for rec in self:
            rec.is_invoice_in_me = False
            if rec.currency_id and rec.currency_id != rec.company_id.currency_id:
                rec.is_invoice_in_me = True
            else:
                rec.is_invoice_in_me = False

    ##########################################################################
    #@api.constrains('date','invoice_date')
    #def _check_reconcile(self):
    #    for rec in self:
    #        if rec.date and rec.invoice_date and rec.date<rec.invoice_date:
    #            raise ValidationError(_("La fecha de Emisión no puede ser mayor a la fecha contable!"))
    ###############################################################################

    def get_information_currency_tc(self):
        for rec in self:
            information_currency_tc = 1.0
            if rec.invoice_date or rec.date and not rec.is_special_tc:
                
                if rec.currency_id and rec.currency_id != rec.company_id.currency_id and rec.move_type in ['out_invoice','in_invoice']:
                    currency_rate_id = self.env['res.currency.rate'].search([
                        ('name', '<=', rec.invoice_date),
                        ('company_id', '=', rec.company_id.id),
                        ('currency_id', '=', rec.currency_id.id)], order="name desc", limit=1)
                    if currency_rate_id:
                        information_currency_tc = currency_rate_id.rate_pe

                elif rec.currency_id and rec.currency_id != rec.company_id.currency_id and rec.move_type in ['in_refund','out_refund']:
                    currency_rate_id = self.env['res.currency.rate'].search([
                        ('name', '<=', rec.reversed_entry_id.invoice_date),
                        ('company_id', '=', rec.company_id.id),
                        ('currency_id', '=', rec.reversed_entry_id.currency_id.id)], order="name desc", limit=1)
                    if currency_rate_id:
                        information_currency_tc = currency_rate_id.rate_pe
                
                elif rec.currency_id and rec.currency_id != rec.company_id.currency_id:
                    currency_rate_id = self.env['res.currency.rate'].search([
                        ('name', '<=', rec.date),
                        ('company_id', '=', rec.company_id.id),
                        ('currency_id', '=', rec.currency_id.id)], order="name desc", limit=1)
                    if currency_rate_id:
                        information_currency_tc = currency_rate_id.rate_pe
            else:
                information_currency_tc = rec.currency_tc

            return information_currency_tc

    ##########################################################################
    @api.onchange('date','invoice_date','currency_id')
    def _onchange_currency(self):
        for rec in self:
            if not rec.is_special_tc:
                super(AccountMove,self)._onchange_currency()

        #_logger.info('\n\nENTRE : _onchange_currency\n\n')
        for rec in self:
            if rec.move_type in ['in_invoice','in_refund'] and rec.currency_id != rec.company_id.currency_id and not rec.is_special_tc:
                if not rec.currency_id:
                    return
                if rec.is_invoice(include_receipts=True):
                    company_currency = rec.company_id.currency_id
                    has_foreign_currency = rec.currency_id and rec.currency_id != company_currency
                    for line in rec._get_lines_onchange_currency():
                        new_currency = has_foreign_currency and rec.currency_id
                        line.currency_id = new_currency
                        line._onchange_currency()
                else:
                    rec.line_ids._onchange_currency()

                rec._recompute_dynamic_lines(recompute_tax_base_amount=True)
    ##########################################################################

    @api.onchange('is_special_tc','currency_id','invoice_date','date')
    def onchange_is_special_tc(self):        
        for rec in self:
            if not rec.is_special_tc:
                #_logger.info('\n\nENTRE : _onchange_is_special_tc\n\n')
                rec.currency_tc = self.get_information_currency_tc()
                for line in rec.line_ids:
                    line._onchange_amount_currency()

    @api.onchange('currency_tc')
    def onchange_currency_tc(self):
        for rec in self:
            for line in rec.line_ids:
                #_logger.info('\n\nENTRE : onchange_currency_tc\n\n')
                line._onchange_amount_currency()

    @api.onchange('currency_id')
    def onchange_currency_id(self):
        for rec in self:
            for line in rec.line_ids:
                #_logger.info('\n\nENTRE : onchange_currency_id\n\n')
                line._onchange_amount_currency()

    @api.constrains('is_special_tc')
    def contrains_not_zero(self):
        if self.is_special_tc:
            if self.currency_tc <= 0.00:
                raise ValidationError(_('El tipo de Cambio no puede ser menor o igual que 0'))

    def _reverse_moves(self, default_values_list=None, cancel=False):
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'is_special_tc': True,
                'currency_tc': move.currency_tc,
            })
        reverse_moves = super()._reverse_moves(default_values_list=default_values_list, cancel=cancel)
        reverse_moves.onchange_currency_tc()
        return reverse_moves


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    currency_tc= fields.Float(related='move_id.currency_tc', string='Tipo de Cambio', digits='Tipo Cambio', store=True)
    is_special_tc = fields.Boolean(string='Tipo Cambio Personalizado', help='Se usó Tipo de Cambio personalizado por el usuario',related='move_id.is_special_tc')

    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:

            company = line.move_id.company_id
            company_currency = line.account_id.company_id.currency_id
            balance = line.amount_currency

            if line.move_id.is_special_tc and line.move_id.currency_tc > 0 and\
                line.currency_id and company_currency and line.currency_id != company_currency:

                #_logger.info('\n\nENTRE : _onchange_amount_currency_1\n\n')
                balance = line.currency_id.with_context(default_pen_rate=self.move_id.currency_tc)._convert(
                    line.amount_currency, company.currency_id, company,
                    line.move_id.date or fields.Date.context_today(line))

            elif not line.move_id.is_special_tc and line.currency_id and company_currency and line.currency_id != company_currency:

                date_rate = line.move_id.invoice_date or line.move_id.date or fields.Date.today()

                #_logger.info('\n\nENTRE : _onchange_amount_currency_2\n\n')
                if line.move_id.move_type in ('in_refund'):
                    date_rate = line.move_id.reversed_entry_id.invoice_date or \
                        line.move_id.reversed_entry_id.date or fields.Date.today()
                elif line.move_id.move_type in ('in_invoice'):
                    date_rate = line.move_id.invoice_date or \
                        line.move_id.date or fields.Date.today()

                balance = line.currency_id._convert(line.amount_currency, company.currency_id, company, date_rate)

            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue
            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())

    ##################################################################################
     ### SE TOMA EL TC A FECHA EMISION COMPROBANTE
    def _recompute_debit_credit_from_amount_currency(self):
        super(AccountMoveLine,self)._recompute_debit_credit_from_amount_currency()
        #_logger.info('\n\nENTRE RECOMPUTE AHORA\n\n')
        for line in self:
            if line.move_id.move_type in ['in_invoice','in_refund'] and not line.move_id.is_special_tc:
            # Recompute the debit/credit based on amount_currency/currency_id and date.
                company_currency = line.account_id.company_id.currency_id
                balance = line.amount_currency
                if line.currency_id and company_currency and line.currency_id != company_currency and not line.move_id.is_special_tc:
                    #_logger.info('\n\nENTRE IF RECOMPUTE\n\n')
                    #### Calculo de Date de Rate
                    date_rate = ''
                    if line.move_id.move_type == 'in_refund':
                        date_rate = line.move_id.reversed_entry_id.invoice_date or \
                            line.move_id.reversed_entry_id.date or fields.Date.today()
                    elif line.move_id.move_type == 'in_invoice':
                        date_rate = line.move_id.invoice_date or \
                            line.move_id.date or fields.Date.today()

                    #balance = line.currency_id._convert(balance, company_currency, line.account_id.company_id,
                    #    line.move_id.invoice_date or line.move_id.date or fields.Date.today())
                    balance = line.currency_id._convert(balance, company_currency, 
                        line.account_id.company_id, date_rate)

                    line.debit = balance > 0 and balance or 0.0
                    line.credit = balance < 0 and -balance or 0.0
    ##########################################################
    @api.model
    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        self.ensure_one()
        ret=super(AccountMoveLine,self)._get_fields_onchange_subtotal()
        if self.move_id.move_type in ['in_invoice','in_refund'] and self.currency_id != self.company_id.currency_id and not self.move_id.is_special_tc:
            #_logger.info('\n\nGET FIELDS ONCHANGE SUBTOTAL\n\n')
            if self.move_id.move_type in ['in_invoice']:
                #_logger.info('\n\nGET FIELDS ONCHANGE SUBTOTAL RETURN\n\n')
                return self._get_fields_onchange_subtotal_model(
                    price_subtotal=price_subtotal or self.price_subtotal,
                    move_type=move_type or self.move_id.move_type,
                    currency=currency or self.currency_id,
                    company=company or self.move_id.company_id,
                    date=date or self.move_id.invoice_date or self.move_id.date,
                )
            elif self.move_id.move_type in ['in_refund','out_refund']:
                date =self.move_id.reversed_entry_id.invoice_date or \
                            self.move_id.reversed_entry_id.date
                return self._get_fields_onchange_subtotal_model(
                    price_subtotal=price_subtotal or self.price_subtotal,
                    move_type=move_type or self.move_id.move_type,
                    currency=currency or self.currency_id,
                    company=company or self.move_id.company_id,
                    date=date or self.move_id.reversed_entry_id.invoice_date or self.move_id.invoice_date or self.move_id.date,
                )
        
        else:
            return ret

    def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
        self.ensure_one()
        #res = super(AccountMoveLine, self)._get_fields_onchange_subtotal(price_subtotal=price_subtotal,move_type=move_type, currency=currency,company=company,date=date)
        if self.move_id.move_type in ['in_refund', 'out_refund']:
            date = self.move_id.reversed_entry_id.invoice_date or \
                            self.move_id.reversed_entry_id.date
        return self._get_fields_onchange_subtotal_model(
            price_subtotal=price_subtotal or self.price_subtotal,
            move_type=move_type or self.move_id.move_type,
            currency=currency or self.currency_id,
            company=company or self.move_id.company_id,
            date=date or self.move_id.date,
        )
