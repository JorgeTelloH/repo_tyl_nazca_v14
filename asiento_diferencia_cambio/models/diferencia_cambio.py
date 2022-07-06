# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DiferenciaCambio(models.Model):
    _name = 'diferencia.cambio'
    _description = "Asiento de Diferencia de Cambio"

    name = fields.Char(string='Referencia', states={'draft': [('readonly', False)]}, required=True)
    date_from = fields.Date(string='Fecha Desde', copy=False, required=True, readonly=True)
    date_to = fields.Date(string='Fecha Hasta', copy=False, required=True, readonly=True)
    date = fields.Date(string='Fecha de Asiento', copy=False, required=True, readonly=True, states={'draft': [('readonly', False)]})
    rate_sale = fields.Float(string='Tipo de Cambio venta', digits=(1, 3), states={'draft': [('readonly', False)]}, required=True)
    rate_purchase = fields.Float(string='Tipo de Cambio Compra', digits=(1, 3), states={'draft': [('readonly', False)]}, required=True)
    company_id = fields.Many2one('res.company', string='Compañía', change_default=True, required=True, readonly=True,
        default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    state = fields.Selection([
            ('draft','Borrador'),
            ('generate', 'Generado'),
        ], string='Estado', index=True, readonly=True, default='draft', copy=False)
    move_id = fields.Many2one(string='Asiento', comodel_name='account.move', readonly=True, copy=False )
    journal_id = fields.Many2one(string='Diario de Diferencia', comodel_name='account.journal', required=True,)

    def action_draft(self):
        for line in self.move_id.line_ids:
            if line.move_line_dc:
                line.remove_move_reconcile()

        self.move_id.button_cancel()
        self.move_id.unlink()
        self.write({'state': 'draft'})


    def action_generate(self):
        if self.move_id.id:
            raise ValidationError(_('Este registro ya tiene un Asiento'))

        if not self.company_id.expense_currency_exchange_account_id.id and not self.company_id.income_currency_exchange_account_id.id:
            raise ValidationError(_('Configure cuentas en el diario ' + self.journal_id.name))

        obj_account = self.env['account.account']
        obj_move = self.env['account.move']
        obj_move_line = self.env['account.move.line']
        list_lines = []

        c_x_c = obj_account.search([('internal_type', '=','receivable'), ('dc_account', '=', True)])
        c_x_p = obj_account.search([('internal_type', '=', 'payable'), ('dc_account', '=', True)])
        c_x_b = obj_account.search([('internal_type', 'not in', ['receivable','payable']), ('dc_account', '=', True)])


        # //// DC para cuentas por cobrar
        account_receivable_ids = c_x_c.ids or c_x_c.id
        receivable_moves_lines = obj_move_line.search(
            [('account_id','in',account_receivable_ids),('amount_residual_currency','!=',0),('credit','=',0),('currency_id','!=',self.company_id.currency_id.id),('reconciled','=',False),('date','>=',self.date_from),('date','<=',self.date_to)])

        #receivable_moves_lines = self.get_post_move_with_payments(receivable_moves_lines, 'receivable')

        if receivable_moves_lines:
            for line in receivable_moves_lines:
                amount_residual_currency = line.amount_residual_currency
                account_id = line.account_id
                move_name = line.move_id.name
                name = line.move_id.name or line.name
                rate_s = self.rate_sale
                rate_p = self.rate_purchase
                partner = line.partner_id.id
                currency = line.currency_id
                monto = line.amount_residual
                balance = self.get_balance(line)
                residual_currency = line.amount_residual_currency
                rate_calculado = round(line.balance / line.amount_currency,3)

                obj, obj2 = self.crate_line(balance, 1, rate_s, rate_p, 'activo', name,
                                            self.journal_id, account_id, partner, currency, move_line=line, residual_currency=residual_currency)
                list_lines.append(obj)
                list_lines.append(obj2)

        # //// DC para cuentas por pagar
        account_payable_ids = c_x_p.ids or c_x_p.id
        payable_moves_lines = obj_move_line.search(
            [('account_id', 'in', account_payable_ids), ('amount_residual_currency', '!=', 0), ('debit', '=', 0),('currency_id','!=',self.company_id.currency_id.id),('reconciled','=',False),('date','>=',self.date_from),('date','<=',self.date_to)])

        #payable_moves_lines = self.get_post_move_with_payments(payable_moves_lines,'payable')

        if payable_moves_lines:
            for line_p in payable_moves_lines:
                amount_residual_currency = line_p.amount_residual_currency
                move_name = line_p.move_id.name
                account_id = line_p.account_id
                name = line_p.move_id.name or line_p.name
                rate_s = self.rate_sale
                rate_p = self.rate_purchase
                partner = line_p.partner_id.id
                currency = line_p.currency_id
                monto = line_p.amount_residual
                balance = self.get_balance(line_p)
                residual_currency = line_p.amount_residual_currency
                rate_calculado = round(line_p.balance / line_p.amount_currency,3)

                obj, obj2 = self.crate_line(balance,
                                            1,
                                            rate_s, rate_p,
                                            'pasivo', name,
                                            self.journal_id,
                                            account_id,
                                            partner,
                                            currency,
                                            move_line=line_p,
                                            residual_currency=residual_currency)


                if obj and obj2:
                    list_lines.append(obj)
                    list_lines.append(obj2)


        # //// DC para otas cuentas
        for account in c_x_b:
            balance, balance_currency = self.get_balance_data_account(account)

            if balance_currency:

                account_id = account
                name = '/'
                rate_s = self.rate_sale
                rate_p = self.rate_purchase
                partner = False
                ##currency = line.currency_id
                monto = balance
                residual_currency = balance_currency
                rate_calculado = round(monto / residual_currency, 3)
                currency = account.currency_id
                obj, obj2 = self.crate_line(monto, 1, rate_s, rate_p, 'activo', name,
                                            self.journal_id, account_id, partner, currency, residual_currency=balance_currency)
                if obj and obj2:
                    list_lines.append(obj)
                    list_lines.append(obj2)

        conver_list = []
        for line in list_lines:
            if round(line['debit'], 2) - round(line['credit'], 2) != 0:
                if round(line['debit'], 2) == 0 and round(line['credit'], 2) == 0:
                    continue
                else:
                    conver_list.append((0, 0, line))

        if len(conver_list) != 0:
            res = {'journal_id': self.journal_id.id,
                   'date': self.date,
                   #'process_account_date': self.date,
                   'ref': self.name,
                   'company_id': self.company_id.id}

            res['line_ids'] = conver_list
            move_id = obj_move.create(res)
            move_id.post()
            for line in move_id.line_ids:
                nn = line.name
                if line.move_line_dc:
                    nann = line.name
                    #line1,line2 =self.get_line_to_reconcile(line,line.move_line_dc)
                    line1 = line
                    line2 = line.move_line_dc
                    #dd = (line+line.move_line_dc).reconcile()
                    dd = (line1+line2).reconcile()


            self.write({'move_id':move_id.id,'state':'generate'})


        else:
            raise ValidationError(_('No existe diferencia de cambio para realizar un asiento'))

        return


    def get_balance(self,line):
        #lines = line.matched_credit_ids+line.matched_debit_ids
        balance = 0
        aml = line
        ids = []
        ids.extend(line)
        if aml.account_id.reconcile:
            ids.extend([r.debit_move_id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id for r in aml.matched_credit_ids])
        for element in ids:
            if element.date <= self.date:
                balance = element.balance + balance
        if not ids:
            balance = line.amount_residual
        return balance

    def get_line_to_reconcile(self,line_generate,line_to_reco):
        ids = []
        aml =line_to_reco
        to_return = False
        sm_debit_move, sm_credit_move = (line_generate+line_to_reco)._get_pair_to_reconcile()
        if not sm_credit_move or not sm_debit_move:
            ids.extend([r.debit_move_id for r in aml.matched_debit_ids] if aml.credit > 0 else [r.credit_move_id for r in aml.matched_credit_ids])
            for element in ids:
                if element.amount_residual:
                    to_return = element

        return line_generate,to_return or aml

    def get_balance_data_account(self, account):


        date_from = fields.Date.to_string(self.date_from)
        date_to = fields.Date.to_string(self.date_to)


        query= """ select sum(debit-credit) balance,  
        sum(amount_currency) balance_currency
        from account_move_line
        join res_currency on account_move_line.currency_id = res_currency.id
        where account_id = %s 
        and  res_currency.name <> 'PEN' 
        and date BETWEEN '%s' and '%s';""" % (account.id,date_from,date_to)

        self.env.cr.execute(query, locals())
        rows = self.env.cr.dictfetchall()
        if rows:
            balance = rows[0].get('balance')
            balance_currency = rows[0].get('balance_currency')
            return balance, balance_currency
        return False, False

    def get_post_move_with_payments(self, list_moves, type):
        recon_obj = self.env['account.partial.reconcile']
        lines_pos = recon_obj.search([('max_date','>',self.date)])
        for line in lines_pos:
            flag = False
            debit_move_id = line.debit_move_id
            credit_move_id = line.credit_move_id
            if type == 'receivable':
                if debit_move_id.account_id.internal_type == type and debit_move_id.credit == 0 and debit_move_id.date < self.date:
                    if debit_move_id not in list_moves:
                        list_moves =list_moves+debit_move_id
            if type == 'payable':
                if credit_move_id.account_id.internal_type == type and credit_move_id.debit == 0 and credit_move_id.date < self.date:
                    if credit_move_id not in list_moves:
                        list_moves =list_moves+credit_move_id

        return list_moves


    def crate_line(self, monto, rate_calculado, rate_s, rate_p, type, name, journal_id, account, partner, currency, move_line=False, residual_currency=False):

        if type == 'activo':
            factor = 1
            # if monto < 0:
            #     monto = monto * -1
            #     factor = -1
            monto2 = residual_currency or monto
            monto_cal = (monto * rate_calculado) - (monto2* rate_p)
            rate = rate_p
            if monto_cal < 0:
                # es mayor el debito y subio la tasa de cambio = ganancias para activo
                return self.create_g(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
                # monto_cal = monto_cal * -1
                # if factor == -1:
                #     return self.create_p(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
                # else:
                #     return self.create_g(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
            elif monto_cal > 0:
                return self.create_p(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
                # if factor == -1:
                #     return self.create_g(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
                # else:
                #     return self.create_p(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
        elif type == 'pasivo':
            # if monto < 0:
            #     monto = monto * -1
            monto2 = residual_currency or monto
            monto_cal = (monto * rate_calculado) - (monto2 * rate_s)
            rate = rate_s
            if monto_cal > 0:
                #monto_cal = monto_cal * -1
                return self.create_p(monto_cal, rate, name, journal_id, account, partner, currency, move_line)
            elif monto_cal < 0:
                return self.create_g(monto_cal, rate, name, journal_id, account, partner, currency, move_line)

        return False, False


    def create_g(self,monto, rate, name, journal_id, account, partner, currency, move_line):
        obj={
            'name':name,
            'debit':0,
            'credit':round(abs(monto),2),
            'account_id':self.company_id.income_currency_exchange_account_id.id,
            'partner_id': partner,
        }
        obj2={
            'name':name,
            'debit':round(abs(monto),2),
            'credit':0,
            'account_id':account.id,
            'amount_currency':0,
            'currency_id': currency.id,
            'partner_id': partner,
        }
        if move_line:
            obj2['move_line_dc'] = move_line.id
        return obj,obj2

    def create_p(self,monto, rate, name, journal_id, account, partner, currency, move_line):

        obj={
            'name':name,
            'debit':round(abs(monto),2),
            'credit':0,
            'account_id':self.company_id.expense_currency_exchange_account_id.id,
            'partner_id': partner,
        }
        obj2={
            'name':name,
            'debit':0,
            'credit':round(abs(monto),2),
            'account_id':account.id,
            'amount_currency': 0,
            'currency_id': currency.id,
            'partner_id': partner,
        }
        if move_line:
            obj2['move_line_dc'] = move_line.id
        return obj,obj2
