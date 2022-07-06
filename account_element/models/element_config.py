# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _

class ElementConfig(models.Model):
	_name = 'element.config'
	_description = "Configuracion de elementos para el informe de estado de situacion"
	_rec_name = "account_balance"

	account_balance = fields.Char(string="Balance General", required=True)
	account_nature = fields.Char(string="Por Naturaleza", required=True)
	account_function = fields.Char(string="Por Funcion", required=True)

	def action_update(self):
		account_balance = (self.account_balance).replace('-','').replace(',','|')
		account_nature = (self.account_nature).replace('-','').replace(',','|')
		account_function = (self.account_function).replace('-','').replace(',','|')
		code = "%s%s%s" %(account_balance,account_nature,account_function)
		self.clear_caches()
		company = self.env.user.company_id
		self._cr.execute("SELECT id FROM account_account WHERE company_id="+str(company.id)+" AND code SIMILAR TO '("+code+")%' ORDER BY code ASC;")
		res_query = [x[0] for x in self._cr.fetchall()]
		account_obj = self.env['account.account'].browse(res_query)
		for account in account_obj:
			account._onchange_type_balance()