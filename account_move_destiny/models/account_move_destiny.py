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
    _name = "account.move.destiny"

    #period_id = fields.Many2one('account.period', string='Periodo', required=True, states={'draft': [('readonly', False)]})
    name = fields.Char(string='Referencia', required = True)
    company_id = fields.Many2one('res.company', string='Compañia', change_default=True,
                                 required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    journal_id = fields.Many2one('account.journal', string='Diario',
                                 required=True, readonly=True, states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Asiento', readonly=True,  copy=False)

    date = fields.Date(string='Fecha de asiento',
                          copy=False,
                          required=True,
                          readonly=True, states={'draft': [('readonly', False)]})

    date_to = fields.Date(string='Fecha desde',
                       copy=False,
                       required = True,
                       readonly=True, states={'draft': [('readonly', False)]})

    date_from = fields.Date(string='Fecha hasta',
                          copy=False,
                          required=True,
                          readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('cancel', 'Cancelled'),
    ], string='Estado', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False)


    def action_open(self):
        move_line = self.env['account.move.line']
        str_to = fields.Date.to_string(self.date_to)
        str_from = fields.Date.to_string(self.date_from)
        query = """ SELECT account_move_line.id id
                    from account_move_line
                    join account_move on account_move_line.move_id = account_move.id
                    join account_account on account_move_line.account_id = account_account.id
                    where account_move.date BETWEEN '%s' AND '%s'
                    and account_account.target_account = True
                    and (account_move_line.target = False or account_move_line.target is NULL) """ % (str_to,str_from)

        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        lines_id = [line.get('id') for line in results]
        if lines_id:
            list_line_move = False
            move_obj = False
            save_move = {'journal_id': self.journal_id.id,
                         'date': self.date,
                         'ref': self.name}
            move_obj = self.env['account.move'].create(save_move)
            account_move_line = self.env['account.move.line']

            lines_move = move_line.browse(lines_id)
            for line in lines_move:
                #list_moves.append(line.id)
                target_debit_id = line.account_id.target_debit_id.id
                target_credit_id = line.account_id.target_credit_id.id
                if line.move_id.company_id.priorise_destiny == 'analitic':
                    if line.analytic_account_id.target_debit_id and line.analytic_account_id.target_credit_id:
                        target_debit_id = line.analytic_account_id.target_debit_id.id
                        target_credit_id = line.analytic_account_id.target_credit_id.id
                    else:
                        continue
                if line.move_id.company_id.priorise_destiny == 'cost_center':
                    if line.cost_center_id.target_debit_id and line.cost_center_id.target_credit_id:
                        target_debit_id = line.cost_center_id.target_debit_id.id
                        target_credit_id = line.cost_center_id.target_credit_id.id
                    else:
                        continue
                amount_currency = line.amount_currency
                if line.analytic_account_id.target_debit_id and line.analytic_account_id.target_credit_id:
                    target_debit_id = line.analytic_account_id.target_debit_id.id
                    target_credit_id = line.analytic_account_id.target_credit_id.id
                if line.debit != 0:
                    obj1 = line.copy_data()[0]
                    obj2 = line.copy_data()[0]
                    obj1.update({'move_id':move_obj.id, 'date': line.date, 'ref': self.name, 'account_id': target_debit_id,'exclude_from_invoice_tab':True})
                    obj2.update({'move_id':move_obj.id, 'debit': False, 'ref': self.name, 'credit': line.debit, 'account_id': target_credit_id, 'amount_currency':amount_currency*-1,'exclude_from_invoice_tab':True})
                    ccp = account_move_line.create([obj1, obj2])
                    if not list_line_move:
                        list_line_move = ccp
                    else:
                        list_line_move += ccp
                    # list_line_move.append(obj1)
                    # list_line_move.append(obj2)
                else:
                    obj1 = line.copy_data()[0]
                    obj2 = line.copy_data()[0]
                    obj1.update({'move_id':move_obj.id, 'date': line.date, 'ref': self.name, 'account_id': target_debit_id,'exclude_from_invoice_tab':True})
                    obj2.update({'move_id':move_obj.id, 'debit': line.credit, 'credit': False, 'date': line.date, 'ref': self.name, 'account_id': target_credit_id, 'amount_currency':amount_currency*-1,'exclude_from_invoice_tab':True})
                    ccp = account_move_line.create([obj1, obj2])
                    if not list_line_move:
                        list_line_move = ccp
                    else:
                        list_line_move += ccp

            if list_line_move:
                if lines_move:
                    lines_move.write({'target': True, 'masive_destiny':move_obj.id})


            self.write({'move_id':move_obj.id,
                        'state':'open'})
        return


    def action_cancel(self):
        move = self.env['account.move.line']
        if self.move_id:
            moves = move.search([('masive_destiny','=',self.move_id.id)])
            moves.write({'masive_destiny': False,
                            'target': False})
            self.move_id.unlink()
            self.write({'state': 'cancel'})
        return


    def action_draft(self):
        self.write({'state': 'draft'})
        return



