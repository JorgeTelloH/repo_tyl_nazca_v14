import contextlib
import logging
import json
import requests
import uuid
from unittest.mock import patch
import logging
from odoo import exceptions, _
from odoo.tests.common import BaseCase
from odoo.tools import pycompat
from odoo import models, fields
import hmac
import hashlib
from odoo.exceptions import UserError
import time
from datetime import datetime, timedelta

#_logger = logging.getLogger(__name__)

CURRENCY = {
    'PEN': 1,        # Soles
    'USD': 2,        # Dollars
    'EUR': 3,        # Euros
}

TIPOS_IGV_NUBEFAC_SUNAT = {
'10' : 1,
'11' : 2,
'12' : 3,
'13' : 4,
'14' : 5,
'15' : 6,
'16' : 7,
'20' : 8,
'30' : 9,
'31' : 10,
'32' : 11,
'33' : 12,
'34' : 13,
'35' : 14,
'36' : 15,
'40' : 16,}

tipo_doc = {
    '01':1,
    '03':2,
    '07':3,
    '08':4,
}



def nubefact_jsonrpc(url, method='call', params=None, credentials=None, timeout=15):
    endpoint = credentials.get('enpoint')
    authorization = credentials.get('token')
    timestmap = str(int(time.time()))
    data = json.dumps(params)

    headers = {'Content-type': 'application/json', 'Authorization': authorization}
    try:
        r = requests.post(endpoint, data, headers=headers, verify=True)
    except (
    ValueError, requests.exceptions.ConnectionError, requests.exceptions.MissingSchema, requests.exceptions.Timeout,
    requests.exceptions.HTTPError) as e:
        raise exceptions.AccessError(
            _('The url that this service requested returned an error. Please contact the author of the app. The url it tried to contact was %s',
              url)
        )

    response = r.text
    response = response.replace("'", "\'")
    response = json.loads(response)
    #_logger.info(response)


    ose_accepted = False
    if response.get('errors', False):
        ose_accepted = False
        return {'error': response.get('errors', False)}
    else:
        if response.get('cdr_zip_base64'):
            response['cdr'] = response.get('cdr_zip_base64')
        else:
            response['idFactura'] = "--"

        #response['pdf_url'] = "https://www.nubefact.com/cpe/47695914-6d28-48bf-ae94-ef9e5c4ecd46.pdf"
        if response.get('enlace_del_pdf'):
            response['pdf_url'] = response.get('enlace_del_pdf')

    return response


def nubefact_convert_data(invoice,data_process):
    data = get_header_invoice_nubefact(invoice,data_process)
    #_logger.info("Data: %s", data)
    return data

def get_header_invoice_nubefact(invoice,data_process):

    currency = CURRENCY.get(invoice.currency_id.name, False)
    numero_doc = invoice.name.replace(' ', '')
    if not currency:
        raise UserError(
            _('Moneda \'%s, %s\' no esta soportada para facturacion electronica. Contactar con el Administrador.') % (
            invoice.currency_id.name, invoice.currency_id.currency_unit_label))
    currency_exchange = invoice.currency_id.with_context(date=invoice.invoice_date)._get_conversion_rate(
        invoice.company_id.currency_id, invoice.currency_id, invoice.env.user.company_id, invoice.invoice_date)
    if currency_exchange == 0:
        raise UserError(
            _('El Tipo de Cambio debe ser diferente de 0.0, Ingresar el tipo de cambio para el  %s') % self.invoice_date)

    portanje_igv = float(invoice._get_percentage_igv())

    total_taxes = round(data_process['tax_details']['total_taxes'], 2)
    total_included = round(data_process['tax_details']['total_included'], 2)
    totalVentaGravada = False
    totalVentaExonerada = 0
    totalVentaInafecta = 0
    sumatoriaIgv = 0
    total_descuento = False
    total_anticipo = False
    total_gratuita = False
    total_otros_cargos = False
    total_isc = False
    total_impuestos_bolsas = False
    montoDetraccion = False
    detraccion_total = False
    porcentajeDetraccion = 0
    medioPago = False
    tipo_documento = tipo_doc.get(invoice.l10n_latam_document_type_id.code)
    invoice_lines = _get_invoice_line_values_odoofact(invoice, data_process)
    data = {}
    for element in data_process['tax_details']['grouped_taxes']:
        if element.get('l10n_pe_edi_tax_code') == '1000':
            totalVentaGravada += element.get('base')
            sumatoriaIgv += element.get('amount')
        if element.get('l10n_pe_edi_tax_code') == '9997':
            totalVentaExonerada += element.get('base')
        if element.get('l10n_pe_edi_tax_code') in ('9998','9995'):
            totalVentaInafecta += element.get('base')

    if invoice.l10n_pe_withhold:
        spot = invoice._l10n_pe_edi_get_spot()
        codigoSujetoDetraccion = invoice.l10n_pe_withhold_code
        numeroCuentaBanco = spot.get('PayeeFinancialAccount')
        medioPago = int(spot.get('PaymentMeansCode'))
        montoDetraccion = spot.get('Amount')
        porcentajeDetraccion = spot.get('PaymentPercent')

    list_cuotas = []
    if invoice.forma_pago == 'Credito':
        num = 1
        for cuota in invoice.cuotas_ids:
            cuota_date = fields.Date.from_string(cuota.date).strftime('%Y-%m-%d')
            list_cuotas.append({
                'cuota': num,
                'fecha_de_pago': datetime.strptime(str(cuota_date), "%Y-%m-%d").strftime("%d-%m-%Y"),
                'importe': abs(cuota.amount),
            })
            num += 1

    if invoice.l10n_pe_edi_operation_type == '0101':
        #Venta Interna
        operation_type = 1
    if invoice.l10n_pe_edi_operation_type == '1001':
        #Operacion sujeta a detraccion
        operation_type = 30
    if invoice.l10n_pe_edi_operation_type == '1002':
        #detraccion - Recursos Hidrobiologicos
        operation_type = 31
    if invoice.l10n_pe_edi_operation_type == '1003':
        #detraccion - Servicio de transporte de pasajeros
        operation_type = 32
    if invoice.l10n_pe_edi_operation_type == '1004':
        #detraccion - Servicio de transporte de carga
        operation_type = 33
    if invoice.l10n_pe_edi_operation_type == '0200':
        #Exportacion de bienes
        operation_type = 2
    if invoice.l10n_pe_edi_operation_type == '2001':
        #Operacion sujeta de Percepcion
        operation_type = 34

    values = {
        'company_id': invoice.company_id.id,
        'l10n_pe_edi_shop_id': False,
        'invoice_id': invoice.id,
        "operacion": "generar_comprobante",
        'tipo_de_comprobante': tipo_documento,
        'serie': numero_doc.split('-')[0],
        'numero': int(numero_doc.split('-')[1]),
        'sunat_transaction': operation_type,
        'cliente_tipo_de_documento': invoice.partner_id.commercial_partner_id.l10n_latam_identification_type_id and invoice.partner_id.commercial_partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '1',
        'cliente_numero_de_documento': invoice.partner_id.commercial_partner_id.vat and invoice.partner_id.commercial_partner_id.vat or '00000000',
        'cliente_denominacion': invoice.partner_id.commercial_partner_id.name or invoice.partner_id.commercial_partner_id.name,
        'cliente_direccion': (invoice.partner_id.street_name or '') \
                             + (invoice.partner_id.street_number or '') \
                             + (invoice.partner_id.street_number2 or '') \
                             + (invoice.partner_id.street2 or '') \
                             + (invoice.partner_id.l10n_pe_district and ', ' + invoice.partner_id.l10n_pe_district.name or '') \
                             + (invoice.partner_id.city_id and ', ' + invoice.partner_id.city_id.name or '') \
                             + (invoice.partner_id.state_id and ', ' + invoice.partner_id.state_id.name or '') \
                             + (invoice.partner_id.country_id and ', ' + invoice.partner_id.country_id.name or ''),
        'cliente_email': invoice.partner_id.email and invoice.partner_id.email or invoice.partner_id.email,
        'fecha_de_emision': datetime.strptime(str(invoice.invoice_date), "%Y-%m-%d").strftime("%d-%m-%Y"),
        'fecha_de_vencimiento': invoice.invoice_date_due and datetime.strptime(str(invoice.invoice_date_due),
                                                                            "%Y-%m-%d").strftime("%d-%m-%Y") or '',
        'moneda': currency,
        'tipo_de_cambio': round(1 / currency_exchange, 3),
        'porcentaje_de_igv': portanje_igv,
        'descuento_global': total_descuento or "",
        'total_descuento': total_descuento or "",
        'total_anticipo': total_anticipo or "",
        'total_gravada': totalVentaGravada or "",
        'total_inafecta': totalVentaInafecta or "",
        'total_exonerada': totalVentaExonerada or "",
        'total_igv': sumatoriaIgv or "",
        'total_gratuita': "",
        'total_otros_cargos': total_otros_cargos or "",
        'total_isc': total_isc and abs(total_isc),
        'total': abs(total_included),
        'retencion_tipo': '',
        'retencion_base_imponible': '',
        'total_retencion': '',
        'total_impuestos_bolsas': total_impuestos_bolsas or "",
        'detraccion': invoice.l10n_pe_withhold and 'true' or 'false',
        'observaciones': invoice.narration or '',
        # 'documento_que_se_modifica_tipo': self.l10n_pe_edi_reversal_type and int(self.l10n_pe_edi_reversal_type) or '',
        # 'documento_que_se_modifica_serie': self.l10n_pe_edi_reversal_serie or '',
        # 'documento_que_se_modifica_numero': self.l10n_pe_edi_reversal_number or '',
        # 'tipo_de_nota_de_credito': self.l10n_pe_edi_reversal_type_id and int(
        #     self.l10n_pe_edi_reversal_type_id.code) or '',
        # 'tipo_de_nota_de_debito': self.l10n_pe_edi_debit_type_id and int(self.l10n_pe_edi_debit_type_id.code) or '',
        'enviar_automaticamente_al_cliente': 'true',
        'codigo_unico': '%s|%s|%s-%s' % (
        'odoo', invoice.company_id.partner_id.vat, numero_doc.split('-')[0], numero_doc.split('-')[1]),
        'condiciones_de_pago': invoice.invoice_payment_term_id and invoice.invoice_payment_term_id.name or '',
        'medio_de_pago': '',
        "orden_compra_servicio": invoice.purchase_order or '',
        "detraccion_tipo": invoice.l10n_pe_withhold_code and int(invoice.l10n_pe_withhold_code) or '',
        "detraccion_total": montoDetraccion or '',
        "detraccion_porcentaje": porcentajeDetraccion or '',
        "medio_de_pago_detraccion": medioPago or '',
        "generado_por_contingencia": 'false',
        'items': invoice_lines,
        'guias': [],
        'venta_al_credito': list_cuotas,
        'provider': 'odoo',
    }
    #Nota de Credito
    if tipo_documento == 3:
        values['documento_que_se_modifica_tipo'] = invoice.reversed_entry_id.l10n_latam_document_type_id.code
        if invoice.reversed_entry_id.name:
            values['documento_que_se_modifica_serie'] = invoice.reversed_entry_id.name.replace(' ', '').split('-')[0]
            values['documento_que_se_modifica_numero'] = invoice.reversed_entry_id.name.replace(' ', '').split('-')[1]
        #Se busca el Catalogo 09 :: Motivos de Nota de Credito
        values['tipo_de_nota_de_credito'] = invoice.l10n_pe_edi_refund_reason
    #Nota de Debito
    if tipo_documento == 4:
        values['documento_que_se_modifica_tipo'] = invoice.debit_origin_id.l10n_latam_document_type_id.code
        if invoice.debit_origin_id.name:
            values['documento_que_se_modifica_serie'] = invoice.debit_origin_id.name.replace(' ', '').split('-')[0]
            values['documento_que_se_modifica_numero'] = invoice.debit_origin_id.name.replace(' ', '').split('-')[1]
        #Se busca el Catalogo 10 :: Motivos de Nota de Debito
        values['tipo_de_nota_de_debito'] = invoice.l10n_pe_edi_charge_reason

    if invoice.forma_pago == 'Credito':
        values['medio_de_pago'] = 'venta_al_credito'

    return values


def _get_invoice_line_values_odoofact(invoice,data_process):
    invoice_lines = []
    if not invoice.invoice_line_ids2:
        for element in data_process.get('invoice_lines_vals'):
            line = element.get('line')
            line_tax_detail = element.get('tax_details')
            tax = line.tax_ids
            valorUnitario = 0
            if tax.price_include:
                valorUnitario = line.price_subtotal / line.quantity
            else:
                valorUnitario = line.price_unit

            tipoafectacionigv_val = tax.l10n_pe_edi_affectation_reason
            codigotributo_val = tax.l10n_pe_edi_tax_code

            baseafectacionigv_val = line.price_subtotal
            montoafectacionigv_val = porcentajeimpuesto_val = 0
            if tax.l10n_pe_edi_tax_code == '1000':
                montoafectacionigv_val = baseafectacionigv_val * (tax.amount / 100)
                porcentajeimpuesto_val = tax.amount

            values = {
                'unidad_de_medida': line.product_uom_id.l10n_pe_edi_measure_unit_code,
                'codigo': line.product_id and line.product_id.default_code or '',
                'descripcion': line.name,
                'cantidad': abs(line.quantity),
                'valor_unitario': abs(valorUnitario),
                'precio_unitario': abs(line_tax_detail.get('unit_total_included')),
                'descuento': "",
                'subtotal': abs(line.price_subtotal),
                'tipo_de_igv': TIPOS_IGV_NUBEFAC_SUNAT.get(tipoafectacionigv_val),
                'igv': abs(round(montoafectacionigv_val,2)),
                "impuesto_bolsas": abs(0),
                'total': abs(line.price_total),
                'anticipo_regularizacion': 'false',
                'anticipo_documento_serie': '',
                'anticipo_documento_numero': '',
                'codigo_producto_sunat': line.product_id.unspsc_code_id and line.product_id.unspsc_code_id.code or '',
                "tipo_de_isc": '',
                "isc": abs(0),
            }
            invoice_lines.append(values)


    return invoice_lines
