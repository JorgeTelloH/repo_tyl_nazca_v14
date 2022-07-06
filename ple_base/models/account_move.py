# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError

class AccountMove(models.Model):
	_inherit = 'account.move'

	declared_ple = fields.Boolean(string="Registro declarado" , copy=False)
	### CAMPO PARA EVITAR QUE LAS FACTURAS O BOLETAS DECLARADAS EN EL PLE SEAN ELIMINADAS

	## HABILITAR ESOS METODOS, SON MUY NECESARIOS, SOLO SE DESABILITARON TEMPORALMENTE !!
	# @api.multi
	# def unlink (self):
	# 	for line in self:
	# 		if line.declared_ple==True:
	# 			raise UserError(_('ESTO(S) ASIENTOS(S) NO SE PUEDE(N) ELIMINAR , YA SE ENCUENTRA(N) DECLARADA(S) EN SU PLE RESPECTIVO !!!'))
	# 		else:
	# 			return super(AccountMove,self).unlink()

	# @api.multi
	# def button_cancel(self):
	# 	if self.declared_ple == True:
	# 		raise UserError(_('ESTE ASIENTO NO SE PUEDE CANCELAR , YA SE ENCUENTRA DECLARADA EN SU PLE RESPECTIVO !!!'))
	# 	else:
	# 		return super(AccountMove,self).button_cancel()

	# @api.one
	# def write(self,object):
	# 	# for line in self:	
	# 	if self.declared_ple == True:
	# 		raise UserError(_('ESTE ASIENTO NO SE PUEDE EDITAR , YA SE ENCUENTRA DECLARADA EN SU PLE RESPECTIVO !!!'))
	# 	else :
	# 		return super(AccountMove,self).write(object)

