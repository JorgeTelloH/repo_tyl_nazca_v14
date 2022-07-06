# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import logging
#_logger=logging.getLogger(__name__)


class ReportPle14(models.Model):
    _name = 'report.ple.14'
    _inherit = ['report.ple']
    _description = 'Registro de Ventas'

    file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    filename_simplified = fields.Char(string='Nombre del archivo simplificado')

    file_txt = fields.Binary(string='Archivo TXT', readonly=True)
    filename_txt = fields.Char(string='Nombre del archivo')
    line_ids = fields.One2many(comodel_name='report.ple.14.line', inverse_name='ple_id', string='Detalle del libro', readonly=True)

    @api.model
    def create(self, vals):
        res = super(ReportPle14, self).create(vals)
        res.update({'name': self.env['ir.sequence'].next_by_code(self._name)})
        return res

    def action_generate(self):
        prefix = "LE"
        company_vat = self.env.user.company_id.partner_id.vat or ''
        date_start = self.date_from
        date_end = self.date_to
        year, month = str(fields.Date().from_string(date_start).year), str(fields.Date().from_string(date_start).month).rjust(2, "0")
        currency = 2 if self.currency_id.name in ['USD'] else 1 #USD=2 /PEN=1
        template = "{}{}{}{}00{}00{}{}{}{}.txt"
        domain = [
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', 'in', ['posted','cancel']),
            ('journal_id.sale_ple', '=', True),
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund'])
        ]
        invoice_obj = self.env['account.move'].search(domain, order='date asc, create_date asc')
        self.create_lines(invoice_obj)
        if self.type_report in ['normal']:
            # sale report normal
            data = self._get_content(self.line_ids)
            filename = template.format(
                prefix, company_vat, year, month, '140100', self.indicator_operation,
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}

        elif self.type_report in ['simplified']:
            # sale report simplified
            filename = template.format(
                prefix, company_vat, year, month, '140200', self.indicator_operation,
                self.indicator_content, currency, 1)
            data = self._get_content_simplified(self.line_ids)
            value = {
                'filename_simplified': filename,
                'file_simplified': base64.encodebytes(data.encode('utf-8'))
            }
        self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            self.env['report.ple.14.line'].create({
                'invoice_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.l10n_pe_operation_type_sunat, x),
                'state_opportunity': '2' if line.state in ['cancel'] else '1'
            })

    @staticmethod
    def _get_content(move_line_obj):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{date_due}|{document_payment_type}|' \
                   '{document_payment_series}|{document_payment_number}|{ticket_fiscal_credit}|' \
                   '{customer_document_type}|{customer_document_number}|{customer_name}|{amount_export}|' \
                   '{amount_untaxed}|{amount_discount_untaxed}|{amount_tax_igv}|{amount_discount_tax_igv}|' \
                   '{amount_tax_exo}|{amount_tax_ina}|{amount_tax_isc}|{amount_rice}|{amount_tax_rice}|{amount_tax_plastic_bag}|{amount_tax_other}|' \
                   '{amount_total}|{currency}|{exchange_currency}|{date_emission_update}|' \
                   '{document_payment_type_update}|{document_payment_series_update}|' \
                   '{document_payment_correlative_update}|{contract_ident}|{type_error_1}|{method_payment}|' \
                   '{state_opportunity}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=line.period,
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                date_due=line.date_due or '',
                document_payment_type=line.document_payment_type or '',
                document_payment_series=line.document_payment_series or '',
                document_payment_number=line.document_payment_number or '',
                ticket_fiscal_credit=line.ticket_fiscal_credit or '',
                customer_document_type=line.customer_document_type or '',
                customer_document_number=line.customer_document_number or '',
                customer_name=line.customer_name or '',
                amount_export=round(line.amount_export, 2) or '0.00',
                amount_untaxed=round(line.amount_untaxed, 2) or '0.00',
                amount_discount_untaxed=round(line.amount_discount_untaxed, 2) or '0.00',
                amount_tax_igv=round(line.amount_tax_igv, 2) or '0.00',
                amount_discount_tax_igv=round(line.amount_discount_tax_igv, 2) or '0.00',
                amount_tax_exo=round(line.amount_tax_exo, 2) or '0.00',
                amount_tax_ina=round(line.amount_tax_ina, 2) or '0.00',
                amount_tax_isc=round(line.amount_tax_isc, 2) or '0.00',
                amount_rice=round(line.amount_rice, 2) or '0.00',
                amount_tax_rice=round(line.amount_tax_rice, 2) or '0.00',
                amount_tax_plastic_bag=round(line.amount_tax_plastic_bag, 2) or '0.00',
                amount_tax_other=round(line.amount_tax_other, 2) or '0.00',
                amount_total=round(line.amount_total, 2) or '0.00',
                currency=line.currency or '',
                exchange_currency= str(format(line.exchange_currency, '.3f')) or '0.000',
                date_emission_update=line.date_emission_update or '',
                document_payment_type_update=line.document_payment_type_update or '',
                document_payment_series_update=line.document_payment_series_update or '',
                document_payment_correlative_update=line.document_payment_correlative_update or '',
                contract_ident=line.contract_ident or '',
                type_error_1=line.type_error_1 or '',
                method_payment=line.method_payment and '1' or '',
                state_opportunity=line.state_opportunity or ''
            )
        return data

    @staticmethod
    def _get_content_simplified(move_line_obj):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{date_due}|{document_payment_type}|' \
                   '{document_payment_series}|{document_payment_number}|{ticket_fiscal_credit}|' \
                   '{customer_document_type}|{customer_document_number}|{customer_name}|{amount_untaxed}|' \
                   '{amount_tax_igv}|{amount_tax_other}|{amount_total}|{currency}|{exchange_currency}|' \
                   '{date_emission_update}|{document_payment_type_update}|{document_payment_series_update}|' \
                   '{document_payment_correlative_update}|{type_error_1}|{method_payment}|{state_opportunity}|\r\n'''
        data = ''
        for line in move_line_obj:
            data += template.format(
                period=line.period,
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                date_due=line.date_due or '',
                document_payment_type=line.document_payment_type or '',
                document_payment_series=line.document_payment_series or '',
                document_payment_number=line.document_payment_number or '',
                ticket_fiscal_credit=line.ticket_fiscal_credit or '',
                customer_document_type=line.customer_document_type or '',
                customer_document_number=line.customer_document_number or '',
                customer_name=line.customer_name or '',
                amount_untaxed=round(line.amount_untaxed, 2) or '0.00',
                amount_tax_igv=round(line.amount_tax_igv, 2) or '0.00',
                amount_tax_other=round(line.amount_tax_other, 2) or '0.00',
                amount_total=round(line.amount_total, 2) or '0.00',
                currency=line.currency or '',
                exchange_currency=line.exchange_currency or '',
                date_emission_update=line.date_emission_update or '',
                document_payment_type_update=line.document_payment_type_update or '',
                document_payment_series_update=line.document_payment_series_update or '',
                document_payment_correlative_update=line.document_payment_correlative_update or '',
                type_error_1=line.type_error_1 or '',
                method_payment=line.method_payment and '1' or '',
                state_opportunity=line.state_opportunity or ''
            )
        return data

class Report14xlxs(models.AbstractModel):
    _name = 'report.report.ple.14'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        sheet = workbook.add_worksheet('{}.xlsx'.format(obj.filename_txt))
        bold_right = workbook.add_format({'bold': True, 'font_color': 'black'})
        bold = workbook.add_format({'bold': True, 'font_color': 'black'})
        normal = workbook.add_format({'font_color': 'black'})
        right = workbook.add_format({'font_color': 'black'})
        left = workbook.add_format({'font_color': 'black'})

        bold.set_align('center')
        bold_right.set_align('right')
        normal.set_align('center')
        left.set_align('left')
        right.set_align('right')

        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 20)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 5)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 5)
        sheet.set_column('H:H', 20)
        sheet.set_column('I:I', 35)
        sheet.set_column('J:J', 20)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        sheet.set_column('R:R', 10)
        sheet.set_column('S:S', 10)
        sheet.set_column('T:T', 10)
        sheet.set_column('U:U', 20)
        sheet.set_column('V:V', 15)

        sheet.set_row(6, 30)
        sheet.set_row(7, 25)
        sheet.set_row(8, 30)

        sheet.merge_range('A1:D1', u'FORMATO 14.1: REGISTRO DE VENTAS E INGRESOS', bold_right)
        #sheet.merge_range('A3:B3', u'PERIODO: {}'.format(obj.range_id.name), bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),
                          bold_right)

        sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL REGISTRO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n Y/O PAGO', bold)
        sheet.merge_range('D7:F7', u'COMPROBANTE DE PAGO \nO DOCUMENTO', bold)
        sheet.merge_range('D8:D9', u'TIPO', bold)
        sheet.merge_range('E8:E9', u'Nº SERIE', bold)
        sheet.merge_range('F8:F9', u'NÚMERO', bold)
        sheet.merge_range('G7:I7', u'INFORMACION DEL CLIENTE', bold)
        sheet.merge_range('G8:H8', u'DOCUMENTO DE IDENTIDAD', bold)
        sheet.write('G9', u'TIPO', bold)
        sheet.write('H9', u'NUMERO', bold)
        sheet.merge_range('I8:I9', u'APELLIDOS Y NOMBRES,\nDENOMINACION \nO RAZON SOCIAL', bold)

        sheet.merge_range('J7:J9', u'VALOR \nFACTURADO \nDE LA \nEXPORTACIÓN', bold)
        sheet.merge_range('K7:K9', u'BASE \nIMPONIBLE \nDE LA \nOPERACIÓN \nGRAVADA', bold)

        sheet.merge_range('L7:M8', u'IMPORTE TOTAL \nDE LA OEPRACIÓN \nEXONERADA O INAFECTA', bold)
        sheet.write('L9', u'EXONERADA', bold)
        sheet.write('M9', u'INAFECTA', bold)

        sheet.merge_range('N7:N9', u'ISC', bold)
        sheet.merge_range('O7:O9', u'IGV Y/O IPM', bold)
        sheet.merge_range('P7:P9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        sheet.merge_range('Q7:Q9', u'IMPORTE\nTOTAL DEL \nCOMPROBANTE \nDE PAGO', bold)

        sheet.merge_range('R7:R9', u'TIPO DE \nCAMBIO', bold)

        sheet.merge_range('S7:V7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        sheet.merge_range('S8:S9', u'FECHA', bold)
        sheet.merge_range('T8:T9', u'TIPO', bold)
        sheet.merge_range('U8:U9', u'SERIE', bold)
        sheet.merge_range('V8:V9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)
        sheet.merge_range('W8:W9', u'ESTADO', bold)

        i = 9

        sum = 0.0
        sum2 = 0.0
        sum3 = 0.0
        sum4 = 0.0
        sum5 = 0.0
        sum6 = 0.0
        sum7 = 0.0
        sum8 = 0.0

        for line in obj.line_ids:
            sum += line.amount_export
            sum2 += line.amount_untaxed
            sum3 += line.amount_tax_exo
            sum4 += line.amount_tax_ina
            sum5 += line.amount_tax_isc
            sum6 += line.amount_tax_igv
            sum7 += line.amount_tax_other
            sum8 += line.amount_total

            sheet.write(i, 0, line.move_name, normal)
            sheet.write(i, 1, line.date_emission, normal)
            sheet.write(i, 2, line.date_due, normal)
            sheet.write(i, 3, line.document_payment_type, normal)
            sheet.write(i, 4, line.document_payment_series or '', normal)
            sheet.write(i, 5, line.document_payment_number or '', normal)
            sheet.write(i, 6, line.customer_document_type or '', normal)
            sheet.write(i, 7, line.customer_document_number or '', normal)
            sheet.write(i, 8, line.customer_name, left)
            sheet.write(i, 9, line.amount_export or '0.00', right)
            sheet.write(i + 1, 9, round(sum, 2) or '0.00', bold_right)
            sheet.write(i, 10, line.amount_untaxed or '0.00', right)
            sheet.write(i + 1, 10, round(sum2, 2) or '0.00', bold_right)
            sheet.write(i, 11, line.amount_tax_exo or '0.00', right)
            sheet.write(i + 1, 11, round(sum3, 2) or '0.00', bold_right)
            sheet.write(i, 12, line.amount_tax_ina or '0.00', right)
            sheet.write(i + 1, 12, round(sum4, 2) or '0.00', bold_right)
            sheet.write(i, 13, line.amount_tax_isc or '0.00', right)
            sheet.write(i + 1, 13, round(sum5, 2) or '0.00', bold_right)
            sheet.write(i, 14, line.amount_tax_igv or '0.00', right)
            sheet.write(i + 1, 14, round(sum6, 2) or '0.00', bold_right)
            sheet.write(i, 15, line.amount_tax_other or '0.00', right)
            sheet.write(i + 1, 15, round(sum7, 2) or '0.00', bold_right)
            sheet.write(i, 16, line.amount_total or '0.00', right)
            sheet.write(i + 1, 16, round(sum8, 2) or '0.00', bold_right)
            sheet.write(i, 17, line.exchange_currency, right)
            sheet.write(i, 18, line.date_emission_update, normal)
            sheet.write(i, 19, line.document_payment_type_update, normal)
            sheet.write(i, 20, line.document_payment_series_update, normal)
            sheet.write(i, 21, line.document_payment_correlative_update, normal)
            sheet.write(i, 22, line.state_opportunity, normal)
            i += 1


class PleReport14Line(models.Model):
    _name = 'report.ple.14.line'
    _order = 'date_emission,document_payment_series,document_payment_number'
    _description = 'Detalle de registro de ventas'

    invoice_id = fields.Many2one(comodel_name='account.move', string='Factura')
    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento')
    date_emission = fields.Char(string='Fecha de emisión', compute='_compute_data')
    date_due = fields.Char(string='Fecha de vencimiento', compute='_compute_data')
    document_payment_type = fields.Char(string='Tipo', compute='_compute_data')
    document_payment_series = fields.Char(string='Serie', compute='_compute_data')
    document_payment_number = fields.Char(string='Nro del comprobante', compute='_compute_data')
    ticket_fiscal_credit = fields.Float(string='Operaciones sin derecho fiscal')
    customer_document_type = fields.Char(string='Tipo de DC', compute='_compute_data')
    customer_document_number = fields.Char(string='Número de DC')
    customer_name = fields.Char(string='Cliente', related='invoice_id.partner_id.name')
    amount_export = fields.Float(string='Valor facturado de la exportación', compute='_compute_amount', digits=(12, 2))
    amount_untaxed = fields.Float(string='Base imponible', compute='_compute_amount', digits=(12, 2))
    amount_discount_untaxed = fields.Float(string='Dscto. de la Base imponible', compute='_compute_amount', digits=(12, 2))
    amount_tax_igv = fields.Float(string='IGV y/o IPM', compute='_compute_amount', digits=(12, 2))
    amount_discount_tax_igv = fields.Float(string='Dscto. del IGV y/o IPM', compute='_compute_amount', digits=(12, 2))
    amount_tax_exo = fields.Float(string='Exonerada', compute='_compute_amount', digits=(12, 2))
    amount_tax_ina = fields.Float(string='Inafecta', compute='_compute_amount', digits=(12, 2))
    amount_tax_isc = fields.Float(string='ISC', compute='_compute_amount', digits=(12, 2))
    amount_rice = fields.Float(string='Vta. Arroz Pilado', compute='_compute_amount', digits=(12, 2))
    amount_tax_rice = fields.Float(string='Impuesto Vta. Arroz Pilado', compute='_compute_amount', digits=(12, 2))
    amount_tax_plastic_bag = fields.Float(string='Impuesto Bolsa de Plástico', compute='_compute_amount', digits=(12, 2))
    amount_tax_other = fields.Float(string='Otros conceptos', compute='_compute_amount', digits=(12, 2))
    amount_total = fields.Float(string='Importe Total', compute='_compute_amount', digits=(12, 2))
    currency = fields.Char(string='Moneda', compute='_compute_data')
    exchange_currency = fields.Float(string='Tipo de cambio', compute='_compute_data', digits=(10, 3), store=True)
    date_emission_update = fields.Char(string='Fecha emision de CR', compute='_compute_data')
    document_payment_type_update = fields.Char(string='Tipo de CR', compute='_compute_data')
    document_payment_series_update = fields.Char(string='Serie de CR', compute='_compute_data')
    document_payment_correlative_update = fields.Char(string='Correlativo de CR', compute='_compute_data')
    contract_ident = fields.Char(string='Identificación del contrato')
    type_error_1 = fields.Char(string='Error tipo 1')
    method_payment = fields.Boolean(string='Método de pago', compute='_compute_data')
    state_opportunity = fields.Char(string='Estado')
    ple_id = fields.Many2one(comodel_name='report.ple.14')

    @api.depends('invoice_id')
    def _compute_data(self):

        def get_series_correlative(name):
            #return (name.split('-')[0], name.split('-')[1].rjust(8, '0')) if name and '-' in name else ('', '')
            return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        def get_exhange(inv):
            #exch = self.env['res.currency.rate'].search([('currency_id','=',inv.currency_id.id), ('name','=',inv.invoice_date)])
            curren = self.env['res.currency'].search([('name','=','USD'),('type','=','sale'),('entidad','=','sunat')])
            date = inv.invoice_date
            if inv.move_type == 'out_refund':
                if inv.reversed_entry_id.invoice_date:
                    date = inv.reversed_entry_id.invoice_date

            if inv.is_note_debit and inv.debit_origin_id:
                date = inv.debit_origin_id.invoice_date

            if curren:
                #balance = curren._convert(1, inv.company_currency_id, inv.company_id, date)
                balance = curren._get_conversion_rate(curren,inv.company_currency_id,inv.company_id,date)
            else:
                balance = inv.currency_id._get_conversion_rate(curren,inv.company_currency_id,inv.company_id,date)
            #balance = inv.rate_exchange
            return balance

        def get_year_month(date):
            return '{}{}'.format(str(fields.Date().from_string(date).year), str(fields.Date().from_string(date).month).rjust(2, "0"))

        def get_data_refund(invoice_id):
            if invoice_id.move_type == 'out_refund' and invoice_id.reversed_entry_id:
                code = invoice_id.reversed_entry_id[0].l10n_latam_document_type_id.code
                serie = get_series_correlative(invoice_id.reversed_entry_id[0].name)[0]
                correlative = get_series_correlative(invoice_id.reversed_entry_id[0].name)[1]
                return code,serie, correlative
            if invoice_id.is_note_debit and invoice_id.debit_origin_id:
                code = invoice_id.debit_origin_id.l10n_latam_document_type_id.code
                serie = get_series_correlative(invoice_id.debit_origin_id.name)[0]
                correlative = get_series_correlative(invoice_id.debit_origin_id.name)[1]
                return code, serie, correlative

            return "","",""

        def get_date_emission_update(invoice_id):
            if invoice_id.move_type == 'out_refund' and invoice_id.reversed_entry_id:
                return format_date(invoice_id.reversed_entry_id.invoice_date)
            if invoice_id.is_note_debit and invoice_id.debit_origin_id:
                return format_date(invoice_id.debit_origin_id.invoice_date)

            return False


        self.mapped(lambda x: x.update({
            'period': '{}00'.format(get_year_month(x.invoice_id.date)),
            'cuo': x.invoice_id.name,
            'date_emission': format_date(x.invoice_id.invoice_date),
            'date_due': '01/01/0001', #format_date(x.invoice_id.invoice_date_due) or '',
            'document_payment_type': x.invoice_id.l10n_latam_document_type_id.code or '',
            'document_payment_series': get_series_correlative(x.invoice_id.name)[0],
            'document_payment_number': get_series_correlative(x.invoice_id.name)[1],
            'customer_document_type': x.invoice_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
            'customer_document_number': x.invoice_id.partner_id.vat or '',
            'date_emission_update': get_date_emission_update(x.invoice_id),
            'document_payment_type_update': get_data_refund(x.invoice_id)[0],
            'document_payment_series_update': get_data_refund(x.invoice_id)[1],
            'document_payment_correlative_update': get_data_refund(x.invoice_id)[2],
            'contract_ident': '',
            'type_error_1': '',
            'currency': x.invoice_id.currency_id.name or '',
            'exchange_currency': get_exhange(x.invoice_id),
            'method_payment': x.invoice_id.state in ['paid'] or False
        }))

    @api.depends('invoice_id', 'exchange_currency')
    def _compute_amount(self):

        def get_amount_tax(invoice):
            def compute_tax(p, t, x):
                res = t.compute_all(p, x.invoice_id.currency_id, x.quantity, product=x.product_id,
                                    partner=x.invoice_id.partner_id)
                return res['total_included'] - res['total_excluded']

            data_process = self._l10n_pe_edi_get_edi_values(invoice)
            v_base_imponible = 0
            v_monto_exo = 0
            totalVentaGravada = 0
            totalVentaExonerada = 0
            totalVentaInafecta = 0
            sumatoriaIgv = 0
            amount_export = 0
            amount_total = invoice.amount_total
            isc = 0
            other = 0

            v_base_imponible = round(data_process['tax_details']['total_excluded'], 2)
            igv = round(data_process['tax_details']['total_taxes'], 2)

            for element in data_process['tax_details']['grouped_taxes']:
                if element.get('l10n_pe_edi_tax_code') == '1000':
                    totalVentaGravada += element.get('base')
                    sumatoriaIgv += element.get('amount')
                if element.get('l10n_pe_edi_tax_code') == '9997':
                    totalVentaExonerada += element.get('base')
                if element.get('l10n_pe_edi_tax_code') == '9998':
                    totalVentaInafecta += element.get('base')
                if element.get('l10n_pe_edi_tax_code') == '9995':
                    amount_export += element.get('base')

            if invoice.move_type == 'out_refund':
                v_base_imponible = v_base_imponible *-1
                igv =  igv*-1
                totalVentaGravada =  totalVentaGravada*-1
                totalVentaExonerada =  totalVentaExonerada*-1
                totalVentaInafecta =  totalVentaInafecta*-1
                isc =  isc*-1
                other =  other*-1
                amount_export =  amount_export*-1
                amount_total = amount_total*-1

            if invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.invoice_date
                if invoice.move_type == 'out_refund':
                    date = invoice.reversed_entry_id.invoice_date
                v_base_imponible =  invoice.currency_id._convert(v_base_imponible, invoice.company_id.currency_id, invoice.company_id, date)
                igv = invoice.currency_id._convert(igv, invoice.company_id.currency_id, invoice.company_id, invoice.invoice_date)
                totalVentaGravada = invoice.currency_id._convert(totalVentaGravada, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaExonerada = invoice.currency_id._convert(totalVentaExonerada, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaInafecta = invoice.currency_id._convert(totalVentaInafecta, invoice.company_id.currency_id, invoice.company_id, date)
                isc = invoice.currency_id._convert(isc, invoice.company_id.currency_id, invoice.company_id, invoice.invoice_date)
                other = invoice.currency_id._convert(other, invoice.company_id.currency_id, invoice.company_id, invoice.invoice_date)
                amount_export = invoice.currency_id._convert(amount_export, invoice.company_id.currency_id, invoice.company_id, date)
                amount_total = invoice.currency_id._convert(amount_total, invoice.company_id.currency_id, invoice.company_id, date)

            if invoice.state == 'cancel':
                v_base_imponible = igv = totalVentaGravada = totalVentaExonerada = totalVentaInafecta = isc = other = amount_export = amount_total = 0
            return v_base_imponible, igv, totalVentaGravada, totalVentaExonerada, totalVentaInafecta, isc, other, amount_export, amount_total


        def get_invoice_tax(lines_tax):
            #usamos el impuesto asignado al account_invoice
            igv = exo = inaf = rice = isc = other = 0
            for invtax in lines_tax:
                if invtax.tax_id.tax_sunat.code in ['1000']:
                    igv = igv + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['9997']:
                    exo = exo + invtax.base
                if invtax.tax_id.tax_sunat.code in ['9998']:
                    inaf = inaf + invtax.base
                if invtax.tax_id.tax_sunat.code in ['1016']:
                    rice = rice + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['2000']:
                    isc = isc + invtax.amount
                if invtax.tax_id.tax_sunat.code in ['9999']:
                    other = other + invtax.amount
            return igv, exo, inaf, rice, isc, other


        # def get_discount_amount_untaxed(invoice_id):
        #     discount_amount_untaxed=0
        #     discount_amount_inaf=0
        #     discount_amount_exo=0
        #
        #     if invoice_id.global_discount_type =='percent':
        #         discount_amount_untaxed = get_amount_tax(invoice_id.invoice_line_ids)[0]*(invoice_id.global_discount_rate/100)
        #         discount_amount_inaf = get_amount_tax(invoice_id.invoice_line_ids)[3]*(invoice_id.global_discount_rate/100)
        #         discount_amount_exo = get_amount_tax(invoice_id.invoice_line_ids)[2]*(invoice_id.global_discount_rate/100)
        #
        #     elif invoice_id.global_discount_type=='amount':
        #         rate= invoice_id.global_discount_rate/(get_invoice_tax(invoice_id.tax_line_ids)[0] + get_amount_tax(invoice_id.invoice_line_ids)[0])
        #         discount_amount_untaxed = get_amount_tax(invoice_id.invoice_line_ids)[0]*rate
        #     return discount_amount_untaxed,discount_amount_inaf,discount_amount_exo

        def get_discount_tax(invoice_id):
            discount_tax=0
            if invoice_id.global_discount_type =='percent':
                discount_tax =get_invoice_tax(invoice_id.tax_line_ids)[0]*(invoice_id.global_discount_rate/100)
            elif invoice_id.global_discount_type=='amount':
                rate= invoice_id.global_discount_rate/(get_invoice_tax(invoice_id.tax_line_ids)[0] + get_amount_tax(invoice_id.invoice_line_ids)[0])
                discount_tax = get_invoice_tax(invoice_id.tax_line_ids)[0]*rate
            return discount_tax


        self.mapped(lambda w: w.update({
            'amount_export': get_amount_tax(w.invoice_id)[7],
            'amount_untaxed': 0 if get_amount_tax(w.invoice_id)[7] != 0 else get_amount_tax(w.invoice_id)[0],
            #'amount_discount_untaxed': get_discount_amount_untaxed(w.invoice_id)[0] if get_amount_tax(w.invoice_id.invoice_line_ids)[0]>0.00 else 0.00,
            'amount_discount_untaxed': 0,
            'amount_tax_igv': get_amount_tax(w.invoice_id)[1],
            # 'amount_discount_tax_igv': (get_discount_tax(w.invoice_id))* #get_amount_tax(w.invoice_id.invoice_line_ids)[3] *
            'amount_discount_tax_igv': 0,
            #     (w.invoice_id.currency_id != w.invoice_id.company_id.currency_id and w.invoice_id.move_id.tipocambio or 1) *
            #     (w.invoice_id.type == 'out_refund' and -1 or 1),
            'amount_tax_exo': (get_amount_tax(w.invoice_id)[3]),
            'amount_tax_ina': (get_amount_tax(w.invoice_id)[4]),
            'amount_tax_isc': (get_amount_tax(w.invoice_id)[5]),
            'amount_rice': 0,
            'amount_tax_rice': 0,
            'amount_tax_plastic_bag': 0,
            'amount_tax_other': (get_amount_tax(w.invoice_id)[6]),
            'amount_total': (get_amount_tax(w.invoice_id)[8])
        }))

    def _l10n_pe_edi_get_edi_values(self, invoice):

        def format_float(amount, precision=2):
            ''' Helper to format monetary amount as a string with 2 decimal places. '''
            if amount is None or amount is False:
                return None
            return '%.*f' % (precision, amount)

        def unit_amount(amount, quantity):
            ''' Helper to divide amount by quantity by taking care about float division by zero. '''
            if quantity:
                return invoice.currency_id.round(amount / quantity)
            else:
                return 0.0

        values = {
            'record': invoice,
            'spot': invoice._l10n_pe_edi_get_spot(),
            'PaymentMeansID': invoice._l10n_pe_edi_get_payment_means(),
            'invoice_lines_vals': [],
            'certificate_date': self.env['l10n_pe_edi.certificate']._get_pe_current_datetime().date(),
            'format_float': format_float,
            'tax_details': {
                'total_excluded': 0.0,
                'total_included': 0.0,
                'total_taxes': 0.0,
            },
        }
        tax_details = values['tax_details']

        # Invoice lines.
        tax_res_grouped = {}
        invoice_lines = invoice.invoice_line_ids.filtered(lambda line: not line.display_type)
        for i, line in enumerate(invoice_lines, start=1):
            price_unit_wo_discount = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)

            taxes_res = line.tax_ids.compute_all(
                price_unit_wo_discount,
                currency=line.currency_id,
                quantity=line.quantity,
                product=line.product_id,
                partner=line.partner_id,
                is_refund=invoice.move_type in ('out_refund', 'in_refund'),
            )

            taxes_res.update({
                'unit_total_included': unit_amount(taxes_res['total_included'], line.quantity),
                'unit_total_excluded': unit_amount(taxes_res['total_excluded'], line.quantity),
                'price_unit_type_code': '01' if not line.currency_id.is_zero(price_unit_wo_discount) else '02',
            })
            for tax_res in taxes_res['taxes']:
                tax = self.env['account.tax'].browse(tax_res['id'])
                tax_res.update({
                    'tax_amount': tax.amount,
                    'tax_amount_type': tax.amount_type,
                    'price_unit_type_code': '01' if not line.currency_id.is_zero(tax_res['amount']) else '02',
                    'l10n_pe_edi_tax_code': tax.l10n_pe_edi_tax_code,
                    'l10n_pe_edi_group_code': tax.tax_group_id.l10n_pe_edi_code,
                    'l10n_pe_edi_international_code': tax.l10n_pe_edi_international_code,
                })

                tuple_key = (
                    tax_res['l10n_pe_edi_group_code'],
                    tax_res['l10n_pe_edi_international_code'],
                    tax_res['l10n_pe_edi_tax_code'],
                )

                tax_res_grouped.setdefault(tuple_key, {
                    'base': 0.0,
                    'amount': 0.0,
                    'l10n_pe_edi_group_code': tax_res['l10n_pe_edi_group_code'],
                    'l10n_pe_edi_international_code': tax_res['l10n_pe_edi_international_code'],
                    'l10n_pe_edi_tax_code': tax_res['l10n_pe_edi_tax_code'],
                })
                tax_res_grouped[tuple_key]['base'] += tax_res['base']
                tax_res_grouped[tuple_key]['amount'] += tax_res['amount']

                tax_details['total_excluded'] += tax_res['base']
                tax_details['total_included'] += tax_res['base'] + tax_res['amount']
                tax_details['total_taxes'] += tax_res['amount']

                values['invoice_lines_vals'].append({
                    'index': i,
                    'line': line,
                    'tax_details': taxes_res,
                })

        values['tax_details']['grouped_taxes'] = list(tax_res_grouped.values())

        return values
