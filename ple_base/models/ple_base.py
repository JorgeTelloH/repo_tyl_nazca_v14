# -*- coding: utf-8 -*-
from io import BytesIO
import calendar
from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging
#_logger=logging.getLogger(__name__)

meses=[
	('01','Enero'),
	('02','Febrero'),
	('03','Marzo'),
	('04','Abril'),
	('05','Mayo'),
	('06','Junio'),
	('07','Julio'),
	('08','Agosto'),
	('09','Septiembre'),
	('10','Octubre'),
	('11','Noviembre'),
	('12','Diciembre')]

class PleBase(models.Model):
	_name='ple.base'
	_description = "Modulo base para el PLE Libros SUNAT"

	## PARA CREAR UN NUEVO PLE SOLO SE REQUIERE EL AÑO Y EL MES... LOS OTROS PARAMETROS( IMPRESION Y NOMENCLATURA SOLO SIRVEN PARA IMPRIMIR)
	fiscal_year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2000, (datetime.now().year) + 1 ))] , readonly=True ,  
		states={'draft': [('readonly', False)]}, string="Año Fiscal")
	fiscal_month = fields.Selection(selection=meses, string="Mes Fiscal" ,readonly=True , states={'draft': [('readonly', False)]})
	print_format = fields.Selection(selection='available_formats', string='Formato Impresión:', default='txt')#,
	print_order = fields.Selection(selection='criterios_impresion',string="Criterio Impresión") 
		
	# journal_ids = fields.Many2many('account.journal', 'ple_journal_base_rel', 'journal_id', 'ple_id',readonly=True, states={'draft': [('readonly', False)]},string="Diarios")
	########ATRIBUTOS ADICIONALES !!!
	currency_id = fields.Many2one('res.currency' , string="Impresión en moneda:", default=lambda self: self.env['res.company']._company_default_get('account.invoice').currency_id)
	bimonetario = fields.Boolean(string="Impresión en dos monedas?", default=False)
	currency_second_id = fields.Many2one('res.currency', string="Otra moneda:")
	state = fields.Selection(selection=[('draft','Borrador'),('open','Abierto'),('send','Declarado')],
		readonly=True, states={'draft': [('readonly', False)]}, string="Estado", default="draft")
	company_id = fields.Many2one('res.company',
		string="Compañia", 
		default=lambda self: self.env['res.company']._company_default_get('account.invoice'),
		domain = lambda self: [('id', 'in',[i.id for i in self.env['res.users'].browse(self.env.user.id).company_ids] )],readonly=True)


	# _sql_constraints = [
	# 	('fiscal_month', 'unique(fiscal_month,fiscal_year,company_id)',  'Este periodo para el PLE ya existe , revise sus registros de PLE creados!!!'),
	# ]

	def word_month(self,month):
		meses={
			'01':'ENERO',
			'02':'FEBRERO',
			'03':'MARZO',
			'04':'ABRIL',
			'05':'MAYO',
			'06':'JUNIO',
			'07':'JULIO',
			'08':'AGOSTO',
			'09':'SEPTIEMBRE',
			'10':'OCTUBRE',
			'11':'NOVIEMBRE',
			'12':'DICIEMBRE'}
		return meses[month]

	
	def name_get(self):
		result = []
		for ple in self:
			result.append((ple.id, ple._periodo_fiscal() or 'New'))
		return result

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.search([('fiscal_month', operator, name),('fiscal_year', operator, name)] + args, limit=limit)
		return recs.name_get()

	def _periodo_fiscal(self):
		periodo = "%s%s00" % (self.fiscal_year or 'YYYY', self.fiscal_month or 'MM')
		return periodo

	@api.model
	def criterios_impresion(self):  ## LO RECOMENDABLE ES CONVERTIR ESTO A UN ARRAY !!!! 
		criterios = [
			('nro_documento','N° de registro'), # numero de registro es un consecutivo ## SE TRATA DEL ASIENTO CONTABLE !!
			('date','Fecha de emisión'), # fecha de registro u emision
			# ('invoice_number','N° de documento'),
			# ('prefix_code','N° de serie'),
			# ('table10_id','Tipo de documento')
			]
		return criterios

	# @api.model
	# def criterios_impresion_default(self):  ## LO RECOMENDABLE ES CONVERTIR ESTO A UN ARRAY !!!! 
	# 	#return self.criterios_impresion[0][0] 
	# 	return ('nro_documento','N° de registro')

	#AVAILABLE_FORMAT PADRE
	def available_formats(self):
		formats=[
			('xlsx','xlsx'),
			('txt','txt'),
			('pdf','pdf')]
		return formats

	# INIT_BUFFER PADRE
	def _init_buffer(self, output):
		return output

	# ACTION_PRINT HIJO
	
	def action_print(self):
		return {
			'type': 'ir.actions.act_url',
			'url': 'reports/format/{}/{}/{}'.format(self._name, self.print_format, self.id),
			'target': 'new'
		}

	def action_draft(self):
		for rec in self:
			rec.state="draft"

	def action_open(self):
		for rec in self:
			rec.generar_libro()
			rec.state="open"

	def generar_libro(self):
		for rec in self:
			return True

	def action_send(self):
		for rec in self:
			rec._action_confirm_ple()
			rec.state="send"

	def _action_confirm_ple(self, objet=False, ids=False, dic={'declared_ple':True}):
		for rec in self:
			rec.env[objet].browse(ids).write(dic)
		# self.env[objet].write(dic)
		# return True

	# PRINTER PADRE, retorna el buffer
	def document_print(self):
		output = BytesIO()
		output = self._init_buffer(output)
		output.seek(0)
		return output.read()

	def _get_star_date(self):
		fecha_inicio = "%s-%s-01" %(self.fiscal_year, self.fiscal_month)
		return fecha_inicio

	def _get_end_date(self):
		fecha_fin = "%s-%s-%s" %(self.fiscal_year, self.fiscal_month, calendar.monthrange(int(self.fiscal_year),int(self.fiscal_month))[1])
		return fecha_fin

	def _get_query_datas(self, objet=False, domain=[], order_by=''):
		domain +=  [('company_id','in',[self.company_id.id])]
		return self.env[objet].search(domain + [('company_id','=',self.company_id.id)],order=order_by)

	# def unlink (self):
	# 	for line in self:
	# 		line.write({'declared_ple':False})
	# 		return super(PlaBase, line).unlink()
				# raise UserError(_('ESTA(S) FACTURA(S) NO SE PUEDE(N) ELIMINAR , YA SE ENCUENTRA(N) DECLARADA(S) EN SU PLE RESPECTIVO !!!'))
			# else:
				# return super(AccountInvoice, line).unlink()
	##############IMPRESIÓN DEL REPORTE EN PDF !!
	# 
	# def _print_report(self,report_model):
	# 	if report_model:
	# 		return self.env.ref(report_model).with_context(discard_logo_check=True).report_action(self)
