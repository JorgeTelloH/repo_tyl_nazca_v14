from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
import logging
from itertools import *
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class AccountInvoiceReconcilePayment(models.TransientModel):
	_name = 'account.invoice.reconcile.payment'
	_description = "Conciliación de Facturas Abiertas con Pagos posteados"
	
	criterios=fields.Boolean(string="Búsqueda por criterios",default=False)
	type_invoice=fields.Selection(selection=[('in_invoice','Facturas Proveedor'),('out_invoice','Facturas Cliente'),('all','Todas')])
	date_from=fields.Date(string="Fecha Desde")
	date_to=fields.Date(string="Fecha Hasta")
	currency_id=fields.Many2one('res.currency',string="Moneda de factura")
	partner_ids = fields.Many2many('res.partner','invoice_reconcile_payment_partner_rel','partner_id','payment_id' ,string="Socios")

	facturas_directas=fields.Boolean(string="Selección Directa de Facturas")
	invoice_ids=fields.Many2many('account.invoice','invoice_reconcile_payment_rel','invoice_id','payment_id' ,string="Facturas a pagar",domain="[('residual', '!=',0.00)]")


	@api.onchange('criterios','facturas_directas')
	def onchange_criterios(self):
		if self.criterios:
			self.facturas_directas=False
		else:
			self.facturas_directas=True

	@api.onchange('criterios','facturas_directas')
	def onchange_facturas_directas(self):
		if self.facturas_directas:
			self.criterios=False
		else:
			self.criterios=True


	#@api.multi
	def payment_invoice_massive(self):
		cadena_busqueda=[]
		records=[]
		if self.criterios:

			if len(self.invoice_ids or ''):
				cadena_busqueda.append(('id','in',[i.id for i in self.invoice_ids]))

			if len(self.partner_ids or ''):
				cadena_busqueda.append(('partner_id','in',[i.id for i in self.partner_ids]))
			if self.date_from:
				cadena_busqueda.append(('process_account_date','>=',self.date_from))
			if self.date_to:
				cadena_busqueda.append(('process_account_date','<=',self.date_to))
			if self.currency_id:
				cadena_busqueda.append(('currency_id','in',[self.currency_id.id]))

			if self.type_invoice=='in_invoice':
				cadena_busqueda.append(('type','in',['in_invoice']))
			elif self.type_invoice=='out_invoice':
				cadena_busqueda.append(('type','in',['out_invoice']))
			elif self.type_invoice=='all':
				cadena_busqueda.append(('type','in',['out_invoice','in_invoice']))

			cadena_busqueda.append(('state','in',['open']))
			cadena_busqueda.append(('residual','!=',0.00))

			records= self.env['account.invoice'].search(cadena_busqueda)

		elif self.facturas_directas:
			if len(self.invoice_ids or ''):
				cadena_busqueda.append(('id','in',[i.id for i in self.invoice_ids]))

			records= self.env['account.invoice'].search(cadena_busqueda)

		if not(records or ''):
			raise UserError(_('NO SE ENCONTRARON FACTURAS QUE CUMPLAN LAS CONDICIONES INDICADAS !!'))

		self.payment_massive(records)


	def payment_invoice(self,invoice_id):
		if invoice_id:
			domain=[('communication','=',invoice_id.number),('state', '=', 'posted'),('force_destination_account_id','=',invoice_id.account_id.id)]
			if invoice_id.type in ['in_invoice']:
				domain.append(('payment_type','in',['outbound']))
			elif invoice_id.type in ['out_invoice']:
				domain.append(('payment_type','in',['inbound']))
			payment_id = self.env['account.payment'].search(domain)
			payment_move_line_id = payment_id.mapped('move_line_ids').filtered(lambda t:t.account_id == invoice_id.account_id)
			invoice_move_line_id = invoice_id.move_id.line_ids.filtered(lambda t:t.account_id == invoice_id.account_id)
			if payment_move_line_id:
				(payment_move_line_id + invoice_move_line_id).reconcile()



	def payment_massive(self,invoice_ids):
		if invoice_ids:
			for invoice_id in invoice_ids:
				self.payment_invoice(invoice_id)



			'''if not(records or self.invoice_ids):
				raise UserError(_('NO SE ENCONTRARON FACTURAS QUE CUMPLAN LAS CONDICIONES INDICADAS !!'))

			for factura in records:
				tipo_cambio = self.env['res.currency.rate'].search([('name','=',factura.date_invoice),('company_id','=',factura.company_id.id),('currency_id','=',factura.currency_id.id)], limit=1)
				_logger.info('\n\nTIPO DE CAMBIO\n\n')
				_logger.info(tipo_cambio.rate)
				if tipo_cambio:
					tasa_venta=tipo_cambio.rate
					#if factura.currency_rate != tasa_venta:
					_logger.info('\n\nENTRE AL PRIMER IF !!!\n\n')
					apunte_factura=factura.move_id.line_ids.filtered(lambda f:f.account_id.id == factura.account_id.id)
					if apunte_factura:
						apuntes_conciliados=self._build_matching_tree(apunte_factura)
						_logger.info('\n\nAPUNTES CONCILIADOS\n\n')
						_logger.info(apuntes_conciliados)
						(apunte_factura + apuntes_conciliados).remove_move_reconcile()
						factura.write({'currency_id':factura.company_id.currency_id.id})
						factura.write({'currency_id':self.currency_id.id or factura.currency_id.id})
						#factura.write({'currency_rate':tasa_venta})
						# factura.move_id.button_cancel()
						# factura.move_id.line_ids._onchange_amount_currency()
						self.update_fields_numeric_in_account_move(factura.move_id,tasa_venta)
						#if self.afectar_asientos_conciliados:
						#	self.update_fields_numeric_in_account_move(factura.move_id, tasa_venta)


						if len(apuntes_conciliados or ''):
							# self._update_account_move_line_id_in_payment_detail(factura)
							(apunte_factura + apuntes_conciliados).reconcile()
						# factura.move_id.action_post()'''