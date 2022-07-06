# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import base64
import platform
import os

from odoo.exceptions import UserError


class ReportPle08(models.Model):
    _name = 'report.ple.08'
    _inherit = ['report.ple']
    _description = 'Registro de Compras'

    file_non_domiciled = fields.Binary(string='Archivo TXT no domiciliado', readonly=True)
    filename_non_domiciled = fields.Char(string='Nombre del archivo no simplificado')

    file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    filename_simplified = fields.Char(string='Nombre del archivo simplificado')
    line_ids = fields.One2many(comodel_name='report.ple.08.line', inverse_name='ple_id', string='Detalle del libro', readonly=True)

    @api.model
    def create(self, vals):
        res = super(ReportPle08, self).create(vals)
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
        #Usamos el tipo de Comprobante = FACTURA DE COMPRA / N/C COMPRA / OTROS SEGUN CONFIG EN EL DIARIO
        # s_args = [
        #     ('date_start', '<=', self.range_id.date_start),
        #     ('date_stop', '>=', self.range_id.date_stop),
        #     ('company_id', '=', self.company_id.id),
        # ]
        # date_period = self.env['account.period'].search(s_args)
        # if not date_period:
        #     raise UserError(_('La Fecha ingresada no tiene PERIODO CONTABLE.'))

        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('journal_id.purchase_ple', '=', True),
            ('state', 'in', ['posted']),
            ('company_id', '=', self.company_id.id),
            ('move_type', 'in', ['in_invoice', 'in_refund'])
        ]
        invoice_obj = self.env['account.move'].search(domain, order='date asc, create_date asc')
        self.create_lines(invoice_obj)
        if self.type_report in ['normal']:
            # purchase report normal
            data = self._get_content(self.line_ids, year, month)
            filename = template.format(
                prefix, company_vat, year, month, '080100', self.indicator_operation, 
                self.indicator_content, currency, 1)
            value = {'filename_txt': filename, 'file_txt': base64.encodebytes(data.encode('utf-8'))}
            #value = {'filename_txt': filename, 'file_txt': base64.encodebytes('Hola'.encode('utf-8'))}

            # purchase report non-domiciled
            data = self._get_content_non_domiciled(self.line_ids) #Esto no se usara pero debemos generar el archivo con 01 linea
            filename = template.format(
                prefix, company_vat, year, month, '080200', self.indicator_operation, 
                0, currency, 1) #self.indicator_content, currency, 1) #No debe tener contenido pues el archivo es en blanco
            value.update({'filename_non_domiciled': filename, 'file_non_domiciled': base64.encodebytes(data.encode('utf-8'))})
        elif self.type_report in ['simplified']:
            # purchase report simplified
            filename = template.format(
                prefix, company_vat, year, month, '080300', self.indicator_operation, 
                self.indicator_content, currency, 1)
            data = self._get_content_simplified(self.line_ids, year, month)
            value = {
                'filename_simplified': filename, 
                'file_simplified': base64.encodebytes(data.encode('utf-8'))
            }
        self.action_generate_ple(value)

    def create_lines(self, invoice_obj):
        self.line_ids.unlink()
        for x, line in enumerate(invoice_obj, 1):
            self.env['report.ple.08.line'].create({
                'invoice_id': line.id,
                'ple_id': self.id,
                'move_name': u'{}{}'.format(line.l10n_pe_operation_type_sunat, x)
            })

    @staticmethod
    def _get_content(move_line_obj, v_anio, v_mes):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{date_due}|{document_payment_type}|' \
                '{document_payment_series}|{date_dua}|{document_payment_number}|' \
                '{no_fiscal_credit}|{supplier_document_type}|{supplier_document_number}|' \
                '{supplier_name}|{amount_untaxed1}|{amount_tax_igv1}|{amount_untaxed2}|' \
                '{amount_tax_igv2}|{amount_untaxed3}|{amount_tax_igv3}|' \
                '{amount_exo}|{amount_tax_isc}|{amount_tax_plastic_bag}|{amount_tax_other}|{amount_total}|' \
                '{currency}|{exchange_currency}|{date_emission_update}|{document_payment_type_update}|' \
                '{document_payment_series_update}|{dua_code}|{document_payment_correlative_update}|' \
                '{date_detraction}|{number_detraction}|{retention_mark}|{goods_services_classification}|' \
                '{contract_ident}|{type_error_1}|{type_error_2}|{type_error_3}|{type_error_4}|' \
                '{method_payment}|{state_opportunity}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period= str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                date_due=line.date_due  or '',
                document_payment_type=line.document_payment_type or '',
                document_payment_series=line.document_payment_series or '',
                date_dua=line.date_dua,
                document_payment_number=line.document_payment_number or '',
                no_fiscal_credit=line.no_fiscal_credit or '',
                supplier_document_type=line.supplier_document_type or '',
                supplier_document_number=line.supplier_document_number or '',
                supplier_name=line.supplier_name or '',
                amount_untaxed1=round(line.amount_untaxed1, 2) or '0.00',
                amount_tax_igv1=round(line.amount_tax_igv1, 2) or '0.00',
                amount_untaxed2=round(line.amount_untaxed2, 2) or '0.00',
                amount_tax_igv2=round(line.amount_tax_igv2, 2) or '0.00',
                amount_untaxed3=round(line.amount_untaxed3, 2) or '0.00',
                amount_tax_igv3=round(line.amount_tax_igv3, 2) or '0.00',
                amount_exo=round(line.amount_exo, 2) or '0.00',
                amount_tax_isc=round(line.amount_tax_isc, 2) or '0.00',
                amount_tax_plastic_bag=round(line.amount_tax_plastic_bag, 2) or '0.00',
                amount_tax_other=round(line.amount_tax_other, 2) or '0.00',
                amount_total=round(line.amount_total, 2) or '0.00',
                currency=line.currency or '',
                exchange_currency= str(format(line.exchange_currency, '.3f')) or '0.000',
                date_emission_update=line.date_emission_update or '',
                document_payment_type_update=line.document_payment_type_update or '',
                document_payment_series_update=line.document_payment_series_update or '',
                dua_code=line.dua_code or '',
                document_payment_correlative_update=line.document_payment_correlative_update or '',
                date_detraction=line.date_detraction or '',
                number_detraction=line.number_detraction or '',
                retention_mark=line.retention_mark or '',
                goods_services_classification=line.goods_services_classification or '',
                contract_ident=line.contract_ident or '',
                type_error_1=line.type_error_1 or '',
                type_error_2=line.type_error_2 or '',
                type_error_3=line.type_error_3 or '',
                type_error_4=line.type_error_4 or '',
                method_payment=line.method_payment and '1' or '',
                state_opportunity=line.state_opportunity or ''
            )
        return data

    @staticmethod
    def _get_content_simplified(move_line_obj, v_anio, v_mes):
        template = '{period}|{cuo}|{move_name}|{date_emission}|{date_due}|{document_payment_type}|' \
                '{document_payment_series}|{document_payment_number}|{no_fiscal_credit}|{supplier_document_type}|' \
                '{supplier_document_number}|{supplier_name}|{amount_untaxed1}|{amount_tax_igv1}|' \
                '{amount_tax_other}|{amount_total}|{currency}|{exchange_currency}|' \
                '{date_emission_update}|{document_payment_type_update}|{document_payment_series_update}|' \
                '{document_payment_correlative_update}|{date_detraction}|{number_detraction}|' \
                '{retention_mark}|{goods_services_classification}|{type_error_1}|{type_error_2}|' \
                '{type_error_3}|{method_payment}|{state_opportunity}|\r\n'
        data = ''
        for line in move_line_obj:
            data += template.format(
                period= str(v_anio) + str(v_mes) + "00",
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                date_due=line.date_due or '',
                document_payment_type=line.document_payment_type or '',
                document_payment_series=line.document_payment_series or '',
                document_payment_number=line.document_payment_number or '',
                no_fiscal_credit=line.no_fiscal_credit or '',
                supplier_document_type=line.supplier_document_type or '',
                supplier_document_number=line.supplier_document_number or '',
                supplier_name=line.supplier_name  or '',
                amount_untaxed1=round(line.amount_untaxed1, 2) or '0.00',
                amount_tax_igv1=round(line.amount_tax_igv1, 2) or '0.00',
                amount_tax_other=round(line.amount_tax_other, 2) or '0.00',
                amount_total=round(line.amount_total, 2) or '0.00',
                currency=line.currency or '',
                exchange_currency=line.exchange_currency or '',
                date_emission_update=line.date_emission_update or '',
                document_payment_type_update=line.document_payment_type_update or '',
                document_payment_series_update=line.document_payment_series_update or '',
                document_payment_correlative_update=line.document_payment_correlative_update or '',
                date_detraction=line.date_detraction or '',
                number_detraction=line.number_detraction or '',
                retention_mark=line.retention_mark or '',
                goods_services_classification=line.goods_services_classification or '',
                type_error_1=line.type_error_1 or '',
                type_error_2=line.type_error_2 or '',
                type_error_3=line.type_error_3 or '',
                method_payment=line.method_payment and '1' or '',
                state_opportunity=line.state_opportunity or ''
            )
        return data
    
    @staticmethod
    def _get_content_non_domiciled(move_line_obj):
        #template = '{period}|{cuo}|{move_name}|{date_emission}|{nd_payment_type}|{nd_payment_series}|' \
        #        '{nd_payment_number}|{amount_untaxed}|{amount_other}|{amount_total}|{document_payment_type}|' \
        #        '{document_payment_series}|{dua_year}|{document_payment_number}|{amount_retention_igv}|' \
        #        '{currency}|{exchange_currency}|{supplier_country}|{supplier_name}|' \
        #        '{supplier_address}|{supplier_document_number}|{beneficiary_number}|{beneficiary_name}|' \
        #        '{beneficiary_country}|{linkage}|{income_gross}|{deduction}|{income_net}|{retention_rate}|' \
        #        '{retention_tax}|{agreements_tax}|{exemption_applied}|' \
        #        '{income_type}|{service_modality}|{art_76}|{opportunity_state}\r\n'
        template = '{period}'
        data = ' '
        for line in move_line_obj:
            data += template.format(
                period= '')
            '''data += template.format(
                period=line.period,
                cuo=line.cuo,
                move_name=line.move_name,
                date_emission=line.date_emission,
                nd_payment_type=line.document_payment_type,
                nd_payment_series='',
                nd_payment_number='',
                amount_untaxed='',
                amount_other='',
                amount_total='',
                document_payment_type=line.document_payment_type,
                document_payment_series=line.document_payment_series,
                dua_year='',
                document_payment_number=line.document_payment_number,
                amount_retention_igv='',
                currency=line.currency,
                exchange_currency=line.exchange_currency,
                supplier_country='',
                supplier_name=line.supplier_name,
                supplier_address='',
                supplier_document_number='',
                beneficiary_number='',
                beneficiary_name='',
                beneficiary_country='',
                linkage='',
                income_gross='',
                deduction='',
                income_net='',
                retention_rate='',
                retention_tax='',
                agreements_tax='',
                exemption_applied='',
                income_type='',
                service_modality='',
                art_76='',
                opportunity_state=''
            )'''
            break #Solo imprimir la 1ra linea vacia y salimos
        return data
class Report08xlxs(models.AbstractModel):
    _name = 'report.report.ple.08'
    _inherit ='report.report_xlsx.abstract'

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
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 20)
        sheet.set_column('G:G', 50)
        sheet.set_column('H:H', 5)
        sheet.set_column('I:I', 15)
        sheet.set_column('J:J', 50)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 15)
        sheet.set_column('N:N', 15)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 20)
        sheet.set_column('R:R', 10)
        sheet.set_column('S:S', 10)
        sheet.set_column('T:T', 10)
        sheet.set_column('U:U', 25)
        sheet.set_column('V:V', 15)
        sheet.set_column('W:W', 10)
        sheet.set_column('X:X', 10)
        sheet.set_column('Y:Y', 10)
        sheet.set_column('Z:Z', 5)
        sheet.set_column('AA:AA', 15)
        sheet.set_column('AB:AB', 20)

        sheet.set_row(6, 30)
        sheet.set_row(7, 30)
        sheet.set_row(8, 30)

        sheet.merge_range('A1:B1', u'FORMATO 8.1: "REGISTRO DE COMPRAS"', bold_right)
        #sheet.merge_range('A3:B3', u'PERIODO: {}'.format(obj.range_id.name), bold_right)
        sheet.merge_range('A4:B4', u'RUC: {}'.format(obj.company_id.partner_id.vat), bold_right)
        sheet.merge_range('A5:F5', u'APELLIDOS Y NOMBRES, DENOMINACIÓN O RAZÓN SOCIAL: {}'.format(obj.company_id.name),
                          bold_right)

        sheet.merge_range('A7:A9', u'NÚMERO \nCORRELATIVO \nDEL ASIENTO O \nCÓDIGO ÚNICO DE \nLA OPERACIÓN', bold)
        sheet.merge_range('B7:B9', u'FECHA DE \nEMISION DEL \nCOMPROBANTE DE \nPAGO O DOCUMENT0', bold)
        sheet.merge_range('C7:C9', u'FECHA DE \nVENCIMIENTO\n O FECHA', bold)
        sheet.merge_range('D7:F7', u'COMPROBANTE DE PAGO O DOCUMENTO', bold)
        sheet.merge_range('D8:D9', u'TIPO', bold)
        sheet.merge_range('E8:E9', u'SERIE O CODIGO DE LA \nDEPENDENCIA ADUANERA', bold)
        sheet.merge_range('F8:F9', u'AÑO DE EMISION DE \nLA DUA O DSI', bold)
        sheet.merge_range('G7:G9', u'''Nº DEL COMPROBANTE DE PAGO, DOCUMENTO, \nNº DE ORDEN DEL FORMULARIO FISICO O 
        VIRTUAL,\nNº DE DUA, DSI O \nLIQUIDACION DE COBRANZA \nU OTROS DOCUMENTOS\n EMITIDOS POR SUNAT PARA ACREDITAR\n 
        EL CREDITO FISCAL EN LA IMPORTACION''', bold)
        sheet.merge_range('H7:J7', u'INFORMACION DEL PROVEDOOR', bold)
        sheet.merge_range('H8:I8', u'DOCUMENTO \nDE IDENTIDAD', bold)
        sheet.write('H9', u'TIPO', bold)
        sheet.write('I9', u'NUMERO', bold)
        sheet.merge_range('J8:J9', u'APELLIDOS Y NOMBRES,\nDENOMINACION O \nRAZON SOCIAL', bold)

        sheet.merge_range('K7:L8', u'ADQUISICIONES GRAVADAS \nDESTINADAS A OPERACIONES \nGRAVADAS Y/O EXPORTACIONES',
                          bold)
        sheet.write('K9', u'BASE \nIMPONIBLE', bold)
        sheet.write('L9', u'IGV', bold)

        sheet.merge_range('M7:N8', u'ADQUISICIONES GRAVADAS \nDESTINADAS A OPERACIONES '
                                   u'\nGRAVADAS Y/O EXPORTACION Y \nA OPERACIONES NO GRAVADAS', bold)
        sheet.write('M9', u'BASE \nIMPONIBLE', bold)
        sheet.write('N9', u'IGV', bold)

        sheet.merge_range('O7:P8', u'ADQUISICION GRAVADAS \nDESTINADAS A OPERACIONES \nNO GRAVADAS', bold)
        sheet.write('O9', u'BASE \nIMPONIBLE', bold)
        sheet.write('P9', u'IGV', bold)

        sheet.merge_range('Q7:Q9', u'VALOR DE LAS \nADQUISICIONES \nNO GRAVADAS', bold)
        sheet.merge_range('R7:R9', u'ISC', bold)
        sheet.merge_range('S7:S9', u'OTROS \nTRIBUTOS \nY CARGOS', bold)
        sheet.merge_range('T7:T9', u'IMPORTE\nTOTAL', bold)
        sheet.merge_range('U7:U9', u'Nº DE COMPROBANTE \nDE PAGO EMITIDO \nPOR SUJETO \nNO DOMICILIADO', bold)

        sheet.merge_range('V7:W7', u'CONSTANCIA DE DEPOSITO \nDE DETRACCION', bold)
        sheet.merge_range('V8:V9', u'NUMERO', bold)
        sheet.merge_range('W8:W9', u'FECHA DE \nEMISION', bold)

        sheet.merge_range('X7:X9', u'TIPO DE \nCAMBIO', bold)

        sheet.merge_range('Y7:AB7', u'REFERENCIA DEL COMPROBANTE DE PAGO O \nDOCUMENTO ORIGINAL QUE SE MODIFICA', bold)
        sheet.merge_range('Y8:Y9', u'FECHA', bold)
        sheet.merge_range('Z8:Z9', u'TIPO', bold)
        sheet.merge_range('AA8:AA9', u'SERIE', bold)
        sheet.merge_range('AB8:AB9', u'Nº DEL \nCOMPROBANTE \nDE PAGO O \nDOCUMENTO', bold)

        i = 9

        sum = 0.0
        sum2 = 0.0
        sum3 = 0.0
        sum4 = 0.0
        sum5 = 0.0
        sum6 = 0.0
        sum7 = 0.0
        sum8 = 0.0
        sum9 = 0.0
        sum10 = 0.0

        for line in obj.line_ids:
            sum += line.amount_untaxed1
            sum2 += line.amount_tax_igv1
            sum3 += line.amount_untaxed2
            sum4 += line.amount_tax_igv2
            sum5 += line.amount_untaxed3
            sum6 += line.amount_tax_igv3
            sum7 += line.amount_exo
            sum8 += line.amount_tax_isc
            sum9 += line.amount_tax_other
            sum10 += line.amount_total

            sheet.write(i, 0, line.move_name, normal)
            sheet.write(i, 1, line.date_emission, normal)
            sheet.write(i, 2, line.date_due, normal)
            sheet.write(i, 3, line.document_payment_type, normal)
            sheet.write(i, 4, line.document_payment_series, normal)
            sheet.write(i, 5, line.date_dua, normal)
            sheet.write(i, 6, line.document_payment_number, normal)
            sheet.write(i, 7, line.supplier_document_type, normal)
            sheet.write(i, 8, line.supplier_document_number, normal)
            sheet.write(i, 9, line.supplier_name, normal)
            sheet.write(i, 10, round(line.amount_untaxed1, 2) or '0.00', normal)
            sheet.write(i + 1, 10, round(sum, 2) or '0.00', bold_right)
            sheet.write(i, 11, round(line.amount_tax_igv1, 2) or '0.00', normal)
            sheet.write(i + 1, 11, round(sum2, 2) or '0.00', bold_right)
            sheet.write(i, 12, round(line.amount_untaxed2, 2) or '0.00', normal)
            sheet.write(i + 1, 12, round(sum3, 2) or '0.00', bold_right)
            sheet.write(i, 13, round(line.amount_tax_igv2, 2) or '0.00', normal)
            sheet.write(i + 1, 13, round(sum4, 2) or '0.00', bold_right)
            sheet.write(i, 14, round(line.amount_untaxed3, 2) or '0.00', normal)
            sheet.write(i + 1, 14, round(sum5, 2) or '0.00', bold_right)
            sheet.write(i, 15, round(line.amount_tax_igv3, 2) or '0.00', normal)
            sheet.write(i + 1, 15, round(sum6, 2) or '0.00', bold_right)
            sheet.write(i, 16, round(line.amount_exo, 2) or '0.00', normal)
            sheet.write(i + 1, 16, round(sum7, 2) or '0.00', bold_right)
            sheet.write(i, 17, round(line.amount_tax_isc, 2) or '0.00', normal)
            sheet.write(i + 1, 17, round(sum8, 2) or '0.00', bold_right)
            sheet.write(i, 18, round(line.amount_tax_other, 2) or '0.00', normal)
            sheet.write(i + 1, 18, round(sum9, 2) or '0.00', bold_right)
            sheet.write(i, 19, round(line.amount_total, 2) or '0.00', normal)
            sheet.write(i + 1, 19, round(sum10, 2) or '0.00', bold_right)
            sheet.write(i, 20, "", normal)
            sheet.write(i, 21, line.number_detraction, normal)
            sheet.write(i, 22, line.date_detraction, normal)
            sheet.write(i, 23, line.exchange_currency, normal)
            sheet.write(i, 24, line.date_emission_update, normal)
            sheet.write(i, 25, line.document_payment_type_update, normal)
            sheet.write(i, 26, line.document_payment_series_update, normal)
            sheet.write(i, 27, line.document_payment_correlative_update, normal)
            i += 1


class ReportPle08Line(models.Model):
    _name = 'report.ple.08.line'
    _order = 'date_emission,supplier_document_number,amount_total'
    _description = 'Detalle de registro de compras'

    invoice_id = fields.Many2one(comodel_name='account.move', string='Factura')
    period = fields.Char(string='Periodo', compute='_compute_data')
    cuo = fields.Char(string='CUO', compute='_compute_data')
    move_name = fields.Char(string='Asiento')
    date_emission = fields.Char(string='Fecha de emisión', compute='_compute_data')
    date_due = fields.Char(string='Fecha de vencimiento', compute='_compute_data')
    document_payment_type = fields.Char(string='Tipo', compute='_compute_data')
    document_payment_series = fields.Char(string='Serie', compute='_compute_data')
    date_dua = fields.Integer(string='Año de emisión de la DUA', compute='_compute_data')
    document_payment_number = fields.Char(string='Nro del comprobante', compute='_compute_data')
    no_fiscal_credit = fields.Float(string='Operaciones sin derecho fiscal')
    supplier_document_type = fields.Char(string='Tipo Documento', compute='_compute_data')
    supplier_document_number = fields.Char(string='Nro Documento', compute='_compute_data')
    supplier_name = fields.Char(string='Proveedor', compute='_compute_data')
    amount_untaxed1 = fields.Float(string='Base imponible', compute='_compute_amount', digits=(12, 2))
    amount_tax_igv1 = fields.Float(string='IGV y/o IPM', compute='_compute_amount', digits=(12, 2))
    amount_untaxed2 = fields.Float(string='Base imponible 2', compute='_compute_amount', digits=(12, 2))
    amount_tax_igv2 = fields.Float(string='IGV y/o IPM 2', compute='_compute_amount', digits=(12, 2))
    amount_untaxed3 = fields.Float(string='Base imponible 3', compute='_compute_amount', digits=(12, 2))
    amount_tax_igv3 = fields.Float(string='IGV y/o IPM 3', compute='_compute_amount', digits=(12, 2))
    amount_exo = fields.Float(string='Exonerado', compute='_compute_amount', digits=(12, 2))
    amount_tax_isc = fields.Float(string='ISC', compute='_compute_amount', digits=(12, 2))
    amount_tax_plastic_bag = fields.Float(string='Impuesto Bolsa de Plástico', compute='_compute_amount', digits=(12, 2))
    amount_tax_other = fields.Float(string='Otros conceptos', compute='_compute_amount', digits=(12, 2))
    amount_total = fields.Float(string='Importe Total', compute='_compute_amount', digits=(12, 2))
    currency = fields.Char(string='Moneda', compute='_compute_data')
    exchange_currency = fields.Float(string='Tipo de cambio', compute='_compute_data', digits=(10, 3), store=True)
    date_emission_update = fields.Char(string='Fecha emision de CR', compute='_compute_data')
    document_payment_type_update = fields.Char(string='Tipo de CR', compute='_compute_data')
    document_payment_series_update = fields.Char(string='Serie de CR', compute='_compute_data')
    dua_code = fields.Char(string='Codigo DUA')
    document_payment_correlative_update = fields.Char(string='Nro de CR')
    date_detraction = fields.Char(string='Fecha de detracción', compute='_compute_data')
    number_detraction = fields.Char(string='Constancia de depósito de detracción')
    retention_mark = fields.Char(string='Pago sujeto a retención')
    goods_services_classification = fields.Char(string='Clasificación de los bienes y servicios')
    contract_ident = fields.Char(string='Identificación del contrato')
    type_error_1 = fields.Char(string='Error tipo 1')
    type_error_2 = fields.Char(string='Error tipo 2')
    type_error_3 = fields.Char(string='Error tipo 3')
    type_error_4 = fields.Char(string='Error tipo 4')
    method_payment = fields.Boolean(string='Método de pago', compute='_compute_data')
    state_opportunity = fields.Char(string='Estado', compute='_compute_data')
    ple_id = fields.Many2one(comodel_name='report.ple.08')

    @api.depends('invoice_id')
    def _compute_data(self):
        def get_series_correlative(name):
            return (name.split('-')[0], name.split('-')[1]) if name and '-' in name else ('', '')

        def format_date(date):
            return date and fields.Date().from_string(date).strftime("%d/%m/%Y") or ''

        def get_exhange(inv):
            #exch = self.env['res.currency.rate'].search([('currency_id','=',inv.currency_id.id), ('name','=',inv.invoice_date)])
            if inv.currency_id == inv.company_id.currency_id:
                curren = self.env['res.currency'].search([('name', '=', 'USD'), ('type', '=', 'purchase'), ('entidad','=','sunat')])
            else:
                curren = inv.currency_id

            date = inv.invoice_date
            if inv.move_type == 'in_refund':
                if inv.reversed_entry_id.invoice_date:
                    date = inv.reversed_entry_id.invoice_date

            if inv.is_note_debit and inv.debit_origin_id:
                date = inv.debit_origin_id.invoice_date

            if curren:
                #balance = exch.rate_pe
                #balance = curren._convert(1, inv.company_currency_id, inv.company_id, inv.invoice_date)
                balance = curren._get_conversion_rate(curren, inv.company_currency_id, inv.company_id, date)
            else:
                #balance = inv.currency_id._convert(1, inv.company_currency_id, inv.company_id, inv.invoice_date)
                balance = inv.currency_id._get_conversion_rate(curren, inv.company_currency_id, inv.company_id, date)
            #balance = inv.rate_exchange
            return balance


        def get_year_month(date):
            #return '{}{}'.format(str(date.year), str(date.month).rjust(2, "0"))
            return '{}{}'.format(str(fields.Date().from_string(date).year), str(fields.Date().from_string(date).month).rjust(2, "0"))

        def get_state(in_date_emission, in_date_account, in_number_igv):
            v_state = '6' #Por defecto (dentro de los 12 meses)
            if '{}00'.format(get_year_month(in_date_emission)) == '{}00'.format(get_year_month(in_date_account)):
                if in_number_igv <= 0.00: #El comprobante no da derecho al credito fiscal
                    v_state = '0'
                else: #Si da derecho al credito fiscal
                    v_state = '1'
            else:
                v_dif = in_date_account - in_date_emission
                diferencia = abs(v_dif.days)
                if diferencia > 365:
                    v_state = '7'
            return v_state

        #Funcionalidad que valida que la cadena de texto solo tenga alfabeto / numero y demas es guion
        def validate_number_letter(in_str_text_number):
            out_str_text_number = ''
            if in_str_text_number:
                v_data_str = str(in_str_text_number).upper() #Convertimos en mayusculas
                indice = 0
                while indice < len(v_data_str):
                    #Validamos que el caracter sea alfabeto o es numerico
                    if v_data_str[indice].isalpha() or v_data_str[indice].isdigit():
                        out_str_text_number = out_str_text_number + v_data_str[indice]
                    else:
                        out_str_text_number = out_str_text_number + '-' #Otro Caracter pasa a ser guion
                    indice += 1

            return out_str_text_number

        def get_data_refund(invoice_id):
            if invoice_id.move_type == 'in_refund' and invoice_id.reversed_entry_id:
                code = invoice_id.reversed_entry_id[0].l10n_latam_document_type_id.code
                serie = get_series_correlative(invoice_id.reversed_entry_id[0].ref)[0]
                correlative = get_series_correlative(invoice_id.reversed_entry_id[0].ref)[1]
                return code,serie, correlative
            if invoice_id.is_note_debit and invoice_id.debit_origin_id:
                code = invoice_id.debit_origin_id.l10n_latam_document_type_id.code
                serie = get_series_correlative(invoice_id.debit_origin_id.ref)[0]
                correlative = get_series_correlative(invoice_id.debit_origin_id.ref)[1]
                return code, serie, correlative

            return "","",""

        def get_date_emission_update(invoice_id):
            if invoice_id.move_type == 'in_refund' and invoice_id.reversed_entry_id:
                return format_date(invoice_id.reversed_entry_id.invoice_date)
            if invoice_id.is_note_debit and invoice_id.debit_origin_id:
                return format_date(invoice_id.debit_origin_id.invoice_date)

            return False


        self.mapped(lambda x: x.update({
            'period': '{}00'.format(get_year_month(x.invoice_id.date)),
            'cuo': validate_number_letter(x.invoice_id.name),
            'date_emission': format_date(x.invoice_id.invoice_date),
            'date_due': format_date(x.invoice_id.invoice_date), #format_date(x.invoice_id.invoice_date_due) or '',
            'document_payment_type': x.invoice_id.l10n_latam_document_type_id.code or '',
            'document_payment_series': get_series_correlative(x.invoice_id.ref)[0],
            'date_dua': 0, #fields.Date().from_string(x.invoice_id.date_invoice).year,
            'document_payment_number': get_series_correlative(x.invoice_id.ref)[1],
            'supplier_document_type': x.invoice_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '',
            'supplier_document_number': x.invoice_id.partner_id.vat or '',
            'supplier_name': x.invoice_id.partner_id.name or '',
            'date_emission_update': get_date_emission_update(x.invoice_id),
            'document_payment_type_update': get_data_refund(x.invoice_id)[0],
            'document_payment_series_update': get_data_refund(x.invoice_id)[1],
            'document_payment_correlative_update': get_data_refund(x.invoice_id)[2],
            'currency': x.invoice_id.currency_id.name or '',
            'exchange_currency': get_exhange(x.invoice_id),
            'date_detraction': format_date(x.invoice_id.det_fecpago),
            'number_detraction': x.invoice_id.det_nropago or '',
            'retention_mark': '',
            'goods_services_classification': '',
            'contract_ident': '',
            'type_error_1': '',
            'type_error_2': '',
            'type_error_3': '',
            'type_error_4': '',
            'dua_code': '',
            'state_opportunity': get_state(x.invoice_id.invoice_date, x.invoice_id.date, x.invoice_id.amount_tax),
            'method_payment': x.invoice_id.state in ['paid'] or False
        }))

    @api.depends('invoice_id')
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
            isc = 0
            other = 0
            amount_total = invoice.amount_total

            #v_base_imponible = round(data_process['tax_details']['total_excluded'], 2)

            igv = round(data_process['tax_details']['total_taxes'], 2)

            for element in data_process['tax_details']['grouped_taxes']:
                if element.get('l10n_pe_edi_tax_code') == '1000':
                    totalVentaGravada += element.get('base')
                    sumatoriaIgv += element.get('amount')
                if element.get('l10n_pe_edi_tax_code') == '9997':
                    totalVentaExonerada += element.get('base')
                if element.get('l10n_pe_edi_tax_code') == '9998':
                    totalVentaInafecta += element.get('base')

            v_base_imponible = totalVentaGravada
            if invoice.move_type == 'in_refund':
                v_base_imponible =  v_base_imponible*-1
                igv = igv*-1
                totalVentaGravada =  totalVentaGravada*-1
                totalVentaExonerada =  totalVentaExonerada*-1
                totalVentaInafecta =  totalVentaInafecta*-1
                isc = isc*-1
                other =  other*-1
                amount_total =  amount_total*-1

            if invoice.currency_id != invoice.company_id.currency_id:
                date = invoice.invoice_date
                if invoice.move_type == 'in_refund':
                    date = invoice.reversed_entry_id.invoice_date
                v_base_imponible = invoice.currency_id._convert(v_base_imponible, invoice.company_id.currency_id, invoice.company_id, date)
                igv = invoice.currency_id._convert(igv, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaGravada = invoice.currency_id._convert(totalVentaGravada, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaExonerada = invoice.currency_id._convert(totalVentaExonerada, invoice.company_id.currency_id, invoice.company_id, date)
                totalVentaInafecta = invoice.currency_id._convert(totalVentaInafecta, invoice.company_id.currency_id, invoice.company_id, date)
                isc = invoice.currency_id._convert(isc, invoice.company_id.currency_id, invoice.company_id, date)
                other = invoice.currency_id._convert(other, invoice.company_id.currency_id, invoice.company_id, date)
                amount_total = invoice.currency_id._convert(amount_total, invoice.company_id.currency_id, invoice.company_id, date)
                #exo = exo + v_monto_exo
            return v_base_imponible, igv, totalVentaGravada, totalVentaExonerada, totalVentaInafecta, isc, other, amount_total

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

        self.mapped(lambda w: w.update({
            'amount_untaxed1':  get_amount_tax(w.invoice_id)[0],
            'amount_tax_igv1': get_amount_tax(w.invoice_id)[1],
            'amount_untaxed2': 0,
            'amount_tax_igv2': 0,
            'amount_untaxed3':0,
            'amount_tax_igv3':0,
            'amount_exo': ( get_amount_tax(w.invoice_id)[3] + get_amount_tax(w.invoice_id)[4]),
            'amount_tax_isc': get_amount_tax(w.invoice_id)[5],
            'amount_tax_plastic_bag': 0,
            'amount_tax_other': get_amount_tax(w.invoice_id)[6],
            'amount_total': get_amount_tax(w.invoice_id)[7]
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
            #'spot': invoice._l10n_pe_edi_get_spot(),
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
