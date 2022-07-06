# -*- coding: utf-8 -*-

import time
from collections import OrderedDict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, float_compare
from odoo.tools.safe_eval import safe_eval
from lxml import etree

import logging
_logger = logging.getLogger(__name__)

#----------------------------------------------------------
# Entries
#----------------------------------------------------------


class AccountMove(models.Model):
    _inherit = "account.move"
    
    #target = fields.Boolean(string='Destino Procesado', default=False)
    #masive_destiny = fields.Many2one('account.move', string='Asiento destino masivo', copy=False)

    def _post(self, soft=True):
        #self.mapped('line_ids').create_destiny()
        self.create_destiny()
        res = super(AccountMove, self)._post(soft)
        return res

    def create_destiny(self):
        for move in self:
            if move.company_id.automatic_destiny:
                # Aqui empieza
                list_line_move = []
                list_line_apply = []
                account = self.env['account.account']
                account_move_line = self.env['account.move.line']
                # verifica si existen lineas
                if len(move.line_ids) > 0:
                    # Valida si ya fue ejecutado el amarre en el asiento
                    for l in move.line_ids:
                        if l.target == False:
                            account_id = l.account_id.id
                            if l.account_id.target_account == True:
                                target_debit_id = l.account_id.target_debit_id.id
                                target_credit_id = l.account_id.target_credit_id.id
                                if move.company_id.priorise_destiny == 'analitic':
                                    if l.analytic_account_id.target_debit_id and l.analytic_account_id.target_credit_id:
                                        target_debit_id = l.analytic_account_id.target_debit_id.id
                                        target_credit_id = l.analytic_account_id.target_credit_id.id
                                if move.company_id.priorise_destiny == 'cost_center':
                                        target_debit_id = l.cost_center_id.target_debit_id.id
                                        target_credit_id = l.cost_center_id.target_credit_id.id


                                # Duplica las lineas y las guarda en las variables debe y haber con valores predefinidos, se anulan los campos de "tax" para evitar que se dupliquen los impuestos en el arbol de declaracion de impuestos
                                if l.debit != 0:
                                    amount_currency = l.amount_currency
                                    obj1 = l.copy_data()[0]
                                    obj1.update({'date': l.date, 'ref': l.ref, 'account_id':target_debit_id,'exclude_from_invoice_tab':True})
                                    obj2 = l.copy_data()[0]
                                    obj2.update({'debit':False,'credit':l.debit, 'account_id':target_credit_id,'exclude_from_invoice_tab':True,'amount_currency':amount_currency*-1})
                                    ccp = account_move_line.create([obj1,obj2])
                                    l.target = True

                                else:
                                    amount_currency = l.amount_currency
                                    obj1 = l.copy_data()[0]
                                    obj2 = l.copy_data()[0]
                                    obj1.update({'date': l.date, 'ref': l.ref, 'account_id':target_debit_id,'exclude_from_invoice_tab':True})
                                    obj2.update({'debit': l.credit, 'credit': False,'date':l.date , 'ref':l.ref, 'account_id':target_credit_id,'exclude_from_invoice_tab':True,'amount_currency':amount_currency*-1})
                                    ccp = account_move_line.create([obj1,obj2])
                                    # obj1.write({'date': l.date, 'ref': l.ref, 'account_id':target_debit_id})
                                    # obj2.write({'debit': l.debit, 'credit': False,'date':l.date , 'ref':l.ref, 'account_id':target_credit_id})
                                    l.target = True


        return True

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    target = fields.Boolean(string='Destino Procesado', default=False)
    masive_destiny = fields.Many2one('account.move', string='Asiento destino masivo', copy=False)
