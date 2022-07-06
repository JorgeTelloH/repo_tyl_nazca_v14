# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

def _balance_category(code, elementos):
	res = False
	for b in elementos:
		l = len(b)
		menos = False
		c = code
		if int(b) < 0:
			menos = True
			code = '-%s' %code
		if code[:l] == b and menos:
			res = False
		if not menos and code[:l] == b:
			res = True
		code = c
	return res

class AccountAccount(models.Model):
	_inherit = 'account.account'

	balance_category = fields.Selection(
		selection=[('none', 'Ninguno'),
		('balance', 'Balance'),
		('function', 'Funcion'),
		('nature', 'Naturaleza'),
		('function_nature', 'Naturaleza y Funcion')],
		string=u'Categoría de elemento',
		compute='_onchange_type_balance',
		default='none',
		readonly=True,
		help="Elementos que participan en cada resultado",
		store=True)

	@api.depends('code')
	def _onchange_type_balance(self):
		elmentos = self.env['element.config'].search([],limit=1)
		if elmentos:
			account_balance = elmentos.account_balance.split(',')
			account_nature = elmentos.account_nature.split(',')
			account_function = elmentos.account_function.split(',')
		else:
			account_balance = ['1','2','3','4','5']
			account_nature = ['6','7']
			account_function = ['7','9','69']

		for ac in self:
			if ac.code:
				c = (ac.code).replace(' ','')
				b, f, n = False, False, False
				if _balance_category(c, account_balance):
					ac.balance_category = 'balance'
					b = True
				if _balance_category(c, account_nature):
					ac.balance_category = 'nature'
					n = True
				if _balance_category(c, account_function):
					ac.balance_category = 'function'
					f = True
				if n and f:
					ac.balance_category = 'function_nature'
				if not b and not f and not n:
					ac.balance_category = 'none'

	

class AccountGroup(models.Model):
	_inherit = "account.group"

	level = fields.Selection(selection=[
		('elemento','Elemento'),
		('cuenta','Cuenta'),
		('sub_cuenta','Subcuenta'),
		('divisionaria','Divisionaria'),
		('sub_divisionaria','Sub Divisionaria')],
		string="Nivel")