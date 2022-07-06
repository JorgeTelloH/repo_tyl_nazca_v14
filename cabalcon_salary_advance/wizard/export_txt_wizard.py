# -*- coding: utf-8 -*-
import base64
import time
import datetime
from odoo.tools.config import config
from pathlib import Path
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class ExportTxtWizard(models.TransientModel):
    _name = 'advance.export.txt.wizard'

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Desde', default=time.strftime('%Y-%m-01'), required=True)
    date_to = fields.Date(string='Hasta', default=lambda self: datetime.date.today().replace(day=1) + relativedelta(months=+1, days=-1), required=True)

    def action_print(self):

        def get_amount(value):
            _value = str(value).split('.')
            _int_value = _value[0].zfill(14)
            if _value.__len__() > 1:
                _dec_value = _value[1].zfill(2)
            else:
                _dec_value = ''.zfill(2)
            return _int_value + '.' + _dec_value

        def get_total_contro(cuenta_cargos,advance_ids):
            caracter = '-'
            remplazar = ''
            cuenta_cargos = cuenta_cargos.replace(caracter,remplazar)
            # Obtener desde la posición 4 hasta la longitud
            cuenta_cargos = cuenta_cargos[3:len(cuenta_cargos)]
            ccargos =  float(cuenta_cargos)

            cAbono = 0
            for item in advance_ids:
                cuenta_abono = get_account(item.employee_id)
                cuenta_abono = cuenta_abono.replace(caracter, remplazar)
                if item.employee_id.account_type == 'A':   #Ahorro
                    # Obtener desde la posición 3 hasta la longitud - 3
                    cuenta_abono = cuenta_abono[3:len(cuenta_abono)]
                else:
                    # Obtener desde la posición 10 hasta la longitud
                    cuenta_abono = cuenta_abono[10:len(cuenta_abono)]
                cAbono = cAbono + float(cuenta_abono)
            total = ccargos + cAbono
            _value = str(total).split('.')
            _str_value = _value[0].zfill(15)
            return _str_value


        def get_document_type(value):
            if self.env.ref('cabalcon_hr_documents.document_type_DNI').id == value:
                return '1'
            elif self.env.ref('cabalcon_hr_documents.document_type_CEXT').id == value:
                return '3'
            elif self.env.ref('cabalcon_hr_documents.document_type_PASSPORT').id == value:
                return '4'
            else:
                return ''

        def validate_document(type, value, employee):
            if type == '1':
                if len(value) > 8:
                    raise UserError(
                        'El proceso se interrumpió por que el empleado {} tiene el DNI incorrecto. Por favor rectifíquelo, debe de ser de 8 caracteres'.format(
                            employee.name))
            else:
                if len(value) > 12:
                    if type == '2':
                        _tname = 'Carnet de extrangería'
                    else:
                        _tname = 'Pasaporte'
                    raise UserError(
                        'El proceso se interrumpió por que el empleado {} tiene el {} incorrecto. Por favor rectifíquelo, debe de ser de 1 a 12 caracteres'.format(
                            employee.name, _tname))

            return value.ljust(15)

        def get_account(employee):
            if not employee.bank_account_id:
                raise UserError(
                    'El proceso se interrumpió por que el empleado {} no tiene configurado la cuenta de Abono'.format(
                        employee.name))
            caracter = '-'
            remplazar = ''
            cuenta_cargos = employee.bank_account_id.acc_number.replace(caracter,remplazar)
            return cuenta_cargos

        advance_ids = self.env['salary.advance'].search([('date', '>=', self.date_from),
                                                         ('date', '<=', self.date_to),
                                                         ('state', '=', 'approve')])
        if not advance_ids:
            raise ValidationError('No se encontraron datos para este reporte')

        _date = ''.join(str(self.date_from).split('-'))
        _count = len(advance_ids)
        _total = sum(l.advance for l in advance_ids)
        account_type = advance_ids[0].account_type
        account = advance_ids[0].account

        _file = "Haberes{}.txt".format(_date)
        # data_dir = config['data_dir']
        # file_name = Path(data_dir) / _file
        file_name = _file
        # print(file_name)

        file = open(file_name, 'w', encoding='ISO-8859-1')

        file.write("1")  # primera linea
        file.write(str(_count).zfill(6))  # Cantidad de abonos de la planilla
        file.write(_date)  # Fecha de proceso
        file.write("X")  # Subtipo de Planilla de Haberes
        file.write(account_type)  # Tipo de Cuenta de cargo
        file.write('0001')  # Moneda de la cuenta de cargo
        file.write(account.ljust(20))  # Cuenta de cargo
        file.write(get_amount(_total))  # Monto total de la planilla
        file.write(self.name.ljust(40))  # Referencia de la planilla
        file.write(get_total_contro(account,advance_ids))  # Total de control (checksum)
        file.write("\n")  # Cambio de linea

        for item in advance_ids:
            file.write('2')
            file.write(item.employee_id.account_type)  # Tipo de cuenta
            file.write(get_account(item.employee_id).ljust(20))  # Cuenta de ahorro
            _type = get_document_type(item.employee_id.document_type.id)
            file.write(_type)  # Tipo de documento
            identification = validate_document(_type, item.employee_id.identification_id, item.employee_id)
            file.write(identification)  # Numero del documento
            file.write(item.employee_id.name.ljust(75))  # Nombre del trabajador
            rb = self.env.user.company_id.sigla + " " + "PRIMERA QUINCENA {}".format(item.employee_id.identification_id)
            file.write(rb.ljust(40))
            re = self.env.user.company_id.sigla + " " + "PQ {}".format(item.employee_id.identification_id)
            file.write(re.ljust(20))
            file.write('0001')  # Tipo de moneda
            file.write(get_amount(item.advance))  # Monto del Abono
            file.write('S')  # Validacion
            file.write("\n")  # Cambio de linea

        file.close()

        file_data = open(file_name, 'r', encoding='ISO-8859-1').read()
        values = {
            'name': file_name,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode(file_data.encode('ISO-8859-1')),
        }

        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
