# -*- coding: utf-8 -*-
import time
import base64
from odoo.tools.config import config
from pathlib import Path
from datetime import datetime
from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import UserError, ValidationError


class SalaryAdvancePayment(models.Model):
    _name = "salary.advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Adelanto de salario'

    name = fields.Char(string='Name', readonly=True, default=lambda self: 'Adv/')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  domain=[('contract_id', '!=', False)], help="Employee")
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(), help="Submit date")
    reason = fields.Text(string='Reason', help="Reason")
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    advance = fields.Float(string='Adelanto', required=True)
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    exceed_condition = fields.Boolean(string='Exceed than Maximum',
                                      help="The Advance is greater than the maximum percentage in salary structure")
    department = fields.Many2one('hr.department', string='Department')
    state = fields.Selection([('draft', 'Draft'),
                              ('submit', 'Submitted'),
                              ('waiting_approval', 'Waiting Approval'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled'),
                              ('reject', 'Rejected')], string='Status', default='draft', track_visibility='onchange')
    debit = fields.Many2one('account.account', string='Debit Account')
    credit = fields.Many2one('account.account', string='Credit Account')
    journal = fields.Many2one('account.journal', string='Journal')
    employee_contract_id = fields.Many2one('hr.contract', string='Contract')
    account_type = fields.Selection(string='Tipo de cuenta de cargo',
                                    selection=[('C', 'Corriente'),
                                               ('M', 'Maestra')],
                                    default=lambda self: self.env.user.company_id.account_type)
    account = fields.Char(string='Cuenta de cargo', default=lambda self: self.env.user.company_id.account)
    run_id = fields.Many2one('salary.advance.run', string='lote')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            department_id = self.employee_id.department_id.id
            contract_id = self.employee_id.contract_id.id
            domain = [('employee_id', '=', self.employee_id.id)]
            return {'value': {'department': department_id, 'employee_contract_id': contract_id}, 'domain': {
                'employee_contract_id': domain,
            }}

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },

        }
        return result

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            domain = [('contract_ids.state', 'in', ['open', 'near_expire']),
                      ('contract_ids.date_start', '<=', str(self.date))]
            result = {
                'domain': {
                    'employee_id': domain,
                },
            }
            return result

    def submit_to_manager(self):
        self.state = 'submit'

    def cancel(self):
        self.state = 'cancel'

    def reject(self):
        self.state = 'reject'

    def to_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('salary.advance.seq') or ' '
        res_id = super(SalaryAdvancePayment, self).create(vals)
        return res_id

    def approve_request(self):
        """This Approve the employee salary advance request.
                   """
        emp_obj = self.env['hr.employee']
        # address = emp_obj.browse([self.employee_id.id]).address_home_id
        # if not address.id:
        #     raise UserError('Define home address for the employee. i.e address under private information of the employee.')

        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_month = datetime.strptime(str(self.date), '%Y-%m-%d').date().month
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError('Advance can be requested once in a month')
        if not self.employee_contract_id:
            raise UserError('Define a contract for the employee')
        # struct_id = self.employee_contract_id.struct_id
        struct_id = self.employee_contract_id.structure_type_id.default_struct_id

        adv = self.advance
        amt = self.employee_contract_id.wage
        if adv > amt and not self.exceed_condition:
            raise UserError('Advance amount is greater than allotted')

        if not self.advance:
            raise UserError('You must Enter the Salary Advance amount')
        payslip_obj = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                     ('state', '=', 'done'),
                                                     ('date_from', '<=', self.date),
                                                     ('date_to', '>=', self.date),
                                                     ('refund', '=', False),
                                                     ('credit_note', '=', False)
                                                     ])
        if payslip_obj:
            raise UserError("This month salary already calculated")

        for slip in self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                   ('refund', '=', False),
                                                   ('credit_note', '=', False)]):
            slip_moth = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().month
            if current_month == slip_moth + 1:
                slip_day = datetime.strptime(str(slip.date_from), '%Y-%m-%d').date().day
                current_day = datetime.strptime(str(self.date), '%Y-%m-%d').date().day
                if current_day - slip_day < struct_id.advance_date:
                    raise exceptions.Warning(
                        _('Request can be done after "%s" Days From prevoius month salary') % struct_id.advance_date)
        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """This Approve the employee salary advance request from accounting department.
                   """
        salary_advance_search = self.search([('employee_id', '=', self.employee_id.id), ('id', '!=', self.id),
                                             ('state', '=', 'approve')])
        current_date = datetime.strptime(str(self.date), '%Y-%m-%d').date()
        current_month = current_date.month
        current_year = current_date.year
        for each_advance in salary_advance_search:
            existing_month = datetime.strptime(str(each_advance.date), '%Y-%m-%d').date().month
            if current_month == existing_month:
                raise UserError('Advance can be requested once in a month')
        if not self.debit or not self.credit or not self.journal:
            raise UserError("You must enter Debit & Credit account and journal to approve ")
        if not self.advance:
            raise UserError('You must Enter the Salary Advance amount')

        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            partner_id = False
            if request.employee_id.address_home_id:
                partner_id = request.employee_id.address_home_id.id
            analytic_account_id = False
            if request.employee_id.contract_id.analytic_account_id:
                analytic_account_id = request.employee_id.contract_id.analytic_account_id.id

            reference = 'Adelanto de salario {}/{} de {}'.format(current_month, current_year, request.employee_id.name)
            journal_id = request.journal.id
            move = {
                'narration': 'SALARIO ADELANTADO ' + request_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': partner_id
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'analytic_account_id': analytic_account_id
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'analytic_account_id': analytic_account_id
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move.update({'line_ids': line_ids})
            print("move.update({'line_ids': line_ids})", move.update({'invoice_line_ids': line_ids}))
            draft = move_obj.create(move)
            draft.post()
            self.state = 'approve'
            return True

    def cancel_request_acc_dept(self):

        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        for request in self:
            amount = request.advance
            request_name = request.employee_id.name
            reference = request.name
            journal_id = request.journal.id
            partner_id = False
            if request.employee_id.address_home_id:
                partner_id = request.employee_id.address_home_id.id
            analytic_account_id = False
            if request.employee_id.contract_id.analytic_account_id:
                analytic_account_id = request.employee_id.contract_id.analytic_account_id.id
            move = {
                'narration': 'Cancel Salary Advance Of ' + request_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'partner_id': partner_id
            }

            debit_account_id = request.debit.id
            credit_account_id = request.credit.id

            if debit_account_id:
                debit_line = (0, 0, {
                    'name': request_name,
                    'account_id': debit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'analytic_account_id': analytic_account_id
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': request_name,
                    'account_id': credit_account_id,
                    'journal_id': journal_id,
                    'date': timenow,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'analytic_account_id': analytic_account_id
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move.update({'line_ids': line_ids})
            print("move.update({'line_ids': line_ids})", move.update({'invoice_line_ids': line_ids}))
            draft = move_obj.create(move)
            draft.post()
            self.state = 'cancel'
            return True

    def unlink(self):
        for advance in self:
            if advance.state == 'approve':
                raise ValidationError("No esta permitido borrar el adelanto si ya esta aprobado")
        return super(SalaryAdvancePayment, self).unlink()


class SalaryAdvanceRun(models.Model):
    _name = "salary.advance.run"
    _description = 'Adelanto de salario por lotes'

    name = fields.Char(string='Nombre', required=True)
    date = fields.Date(string='Fecha', required=True, default=lambda self: fields.Date.today())
    reason = fields.Text(string='Rasón', help="Rasón del adelanto")
    debit = fields.Many2one('account.account', string='Cuenta de debito', required=True)
    credit = fields.Many2one('account.account', string='Cuenta de crédito', required=True)
    journal = fields.Many2one('account.journal', string='Diario', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True,
                                 default=lambda self: self.env.user.company_id)
    employee_ids = fields.Many2many('hr.employee', string='Empleados')
    advance_ids = fields.One2many('salary.advance', 'run_id', string='Adelantos')
    advance_count = fields.Integer(compute='_compute_advance_count')
    state = fields.Selection([('draft', 'Borrador'),
                              ('waiting_approval', 'Esperando aprovación'),
                              ('approve', 'Aprobado'),
                              ('cancel', 'Cancelado'),
                              ], string='Estado', default='draft', track_visibility='onchange')
    account_type = fields.Selection(string='Tipo de cuenta de cargo',
                                    selection=[('C', 'Corriente'),
                                               ('M', 'Maestra')],
                                    default=lambda self: self.env.user.company_id.account_type,
                                    required=True)
    account = fields.Char(string='Cuenta de cargo', default=lambda self: self.env.user.company_id.account,
                          required=True)

    def _compute_advance_count(self):
        for run in self:
            run.advance_count = len(run.advance_ids)

    @api.onchange('company_id')
    def onchange_company_id(self):
        company = self.company_id
        domain = [('company_id.id', '=', company.id)]
        result = {
            'domain': {
                'journal': domain,
            },
        }
        return result

    @api.onchange('date')
    def onchange_date(self):
        if self.date:
            domain = [('contract_ids.state', 'in', ['open', 'near_expire']),
                      ('contract_ids.date_start', '<=', str(self.date))]
            result = {
                'domain': {
                    'employee_ids': domain,
                },
            }
            return result

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_generate(self):
        if len(self.employee_ids) == 0:
            raise UserError('Debe seleccionar almenos un empleado')
        self.advance_ids = [(5, 0, 0)]
        for employee in self.employee_ids:
            if employee.contract_id and employee.contract_id.advance > 0:
                values = {'employee_id': employee.id,
                          'employee_contract_id': employee.contract_id.id,
                          'date': self.date,
                          'reason': self.reason,
                          'advance': employee.contract_id.advance,
                          'debit': self.debit.id,
                          'credit': self.credit.id,
                          'journal': self.journal.id,
                          'company_id': self.company_id.id,
                          'run_id': self.id,
                          'department': employee.department_id.id,
                          'account_type': self.account_type,
                          'account': self.account
                          }
                sa = self.env['salary.advance'].create(values)
                sa.approve_request()
            else:
                raise UserError(
                    'El proceso se interrumpió por que el empleado {} no tiene contrato o el adelanto no esta configurado'.format(
                        employee.name))
            self.write({'state': 'waiting_approval'})

    def approve_for_acc_dept(self):
        for sa in self.advance_ids:
            sa.approve_request_acc_dept()
        self.write({'state': 'approve'})

    def action_cancel(self):
        for sa in self.advance_ids:
            sa.cancel_request_acc_dept()
        self.write({'state': 'cancel'})

    def action_open_advance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "salary.advance",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.advance_ids.ids]],
            "name": "Adelantos",
        }

    def unlink(self):
        for advance in self:
            if advance.state == 'approve':
                raise ValidationError("No esta permitido borrar el lote si ya esta aprobado")
        return super(SalaryAdvanceRun, self).unlink()

    def action_print_txt(self):

        def get_amount(value):
            _value = str(value).split('.')
            _int_value = _value[0].zfill(14)
            if _value.__len__() > 1:
                _dec_value = _value[1].zfill(2)
            else:
                _dec_value = ''.zfill(2)
            return _int_value + '.' + _dec_value
        
        def get_total_contro(cuenta_cargos, advance_ids):
            caracter = '-'
            remplazar = ''
            cuenta_cargos = cuenta_cargos.replace(caracter, remplazar)
            # Obtener desde la posición 4 hasta la longitud
            cuenta_cargos = cuenta_cargos[3:len(cuenta_cargos)]
            ccargos = float(cuenta_cargos)

            cAbono = 0
            for item in advance_ids:
                cuenta_abono = get_account(item.employee_id)
                cuenta_abono = cuenta_abono.replace(caracter, remplazar)
                if item.employee_id.account_type == 'A':  # Ahorro
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
            if type == 1:
                if len(value) > 8 or len(value) < 8:
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
            return employee.bank_account_id.acc_number.ljust(20)

        _date = ''.join(str(self.date).split('-'))
        _count = len(self.advance_ids)
        _total = sum(l.advance for l in self.advance_ids)
        account_type = self.advance_ids[0].account_type
        account = self.advance_ids[0].account

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
        file.write(self.account_type)  # Tipo de Cuenta de cargo
        file.write('0001')  # Moneda de la cuenta de cargo
        file.write(account.ljust(20))  # Cuenta de cargo
        file.write(get_amount(_total))  # Monto total de la planilla
        file.write(self.name.ljust(40))  # Referencia de la planilla
        file.write(get_total_contro(account, self.advance_ids))  # Total de control (checksum)
        file.write("\n")  # Cambio de linea

        for item in self.advance_ids:
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
