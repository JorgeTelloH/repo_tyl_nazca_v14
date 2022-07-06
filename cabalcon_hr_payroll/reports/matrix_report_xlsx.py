# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields
from odoo.exceptions import UserError, ValidationError


class MatrixReportXlsx(models.AbstractModel):
    _name = "report.cabalcon_hr_payroll.matrix_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte modelo de contabilidad"

    def get_sum(seft, col, init_row, end_row):
        return "=SUM({}{}:{}{})".format(col, init_row, col, end_row)

    def get_sum_aporte(seft, row):
        return "=AR{} + AT{} + AV{}".format(row, row, row)

    def get_sum_ingreso(seft, row):
        return "=N{} + O{} + P{} + R{} + U{} + X{} + Y{} + AB{} + AC{} + AD{} + AE{} + AF{} + Z{} + AA{} + Q{}".format(row, row, row, row, row, row, row, row, row, row, row, row, row, row, row)

    def get_sum_imponible(seft, row):
        return "=N{}+O{}+P{}+R{}+U{}+X{}+Y{}+AB{}+AC{}+AE{}-AE{}-AB{}-Y{}+Q{}-R{}".format(row, row, row, row, row, row, row, row, row, row, row, row, row, row, row)

    def get_sum_neto_a_pagar(seft, row):
        return "=AG{} + AX{}".format(row, row)

    def get_sum_descuento(seft, row):
        return "=AJ{} + AK{} + AL{} + AM{} + AN{} + AO{} + AP{} + AW{}".format(row, row, row, row, row, row, row, row)
    # SUMAR.SI(H8:H59,B65,AW8:AW59)
    def get_sum_afp(self, row, init_row, end_row):
        return "=SUMIF(H{}:H{},B{},AW{}:AW{})".format(init_row,end_row, row, init_row, end_row)

    def get_factor_rd_dd(self, row):
        return "=L{}/30/30".format(row)

    def get_factor(self, row):
        return "=BQ{}*BP{}".format(row, row)

    # funcion para saber si es un nuevo ingreso
    def labor_relation_started(seft, ddate, _date):
        if _date.year == ddate.year and _date.month == ddate.month:
            return True
        else:
            return False
    # funcion para saver si termino en este periodo
    def labor_relation_finished(self, ddate, _date):
        if ddate and _date.year == ddate.year and _date.month == ddate.month:
            return True
        else:
            return False

    # obtener la imformacion de las vacaciones
    def get_vacations(self, employee_id, date_from, date_to):
        holiday_status_id = self.env.ref('cabalcon_hr_holidays.holiday_status_vac')
        holidays = self.env['hr.leave'].sudo().search([
            ('employee_id', '=', employee_id),
            ('holiday_status_id', '=', holiday_status_id.id),
            ('state', 'in', ['confirm', 'validate']),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
        ], limit=1)
        values = {}
        if holidays:
            values['date_from'] = holidays.date_from.date()
            values['date_to'] = holidays.date_to.date()
            values['days'] = holidays.number_of_days
        return values

    def get_commission(seft, col):
        return "=AH{}*AS{}/100".format(col, col)

    def get_total_aportaciones(seft, col):
        return "=BA{} + BC{}".format(col, col)

    def get_otros_seguro(seft, col):
        return "=BE{} - BG{}".format(col, col)

    def generate_xlsx_report(self, workbook, data, employees):

        contracts = self.env['hr.contract'].browse(data['data_report'])
        date_from = data['date_from']
        date_to = data['date_to']
        company = self.env['res.company'].browse(data['company_id'])
        _date = fields.Date.to_date(date_from)

        bold = workbook.add_format({"bold": True, 'valign': 'vcenter', 'text_wrap': True, "align": "center", 'fg_color': '#00FFFF', 'border': 1})
        sheet = workbook.add_worksheet('MATRIZ')

        format1 = workbook.add_format({'font_size': 20, 'align': 'vcenter', 'bold': True})
        h1 = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'bottom', 'bold': True, 'text_wrap': True, 'fg_color': '#00FFFF',  'border': 1})
        h2 = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'bottom', 'bold': True, 'text_wrap': True, 'fg_color': '#2cff00', 'border': 1})
        format2 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        fdate = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        headers1 = ['', '', '', 'CUENTA',  'FECHA', '', 'FECHA', '', 'TIPO DE', '',
                   'CENTRO', '', '', 'Remuneración', '',
                   '', 'Vacaciones', '', '', '', '',
                   '', '', '', '', 'Gratificación', 'Bonificacción',
                   'SUBSIDIO POR', 'Asigna', '', '', '',
                   'TOTAL', 'TOTAL', '', '', '5TA', 'RETENCION',
                   'OTROS', 'ADELANTOS', 'OTROS', 'PRIMERA','','','','',
                    '', '', 'TOTAL', 'TOTAL', 'NETO A', '', '', '', '',
                    'TOTAL A', '', 'CREDITO', 'IMPOTTE', '', '', 'DIAS', '',
                    ]

        headers21 = ['', '', '', '', 'CANTIDAD DE', 'FACTOR DE DESCUENTO', 'FACTOR DE DESCUENTO', '', '', '']

        headers2 = ['COD', 'APELLIDOS Y NOMBRES', 'CARGO', 'REMUNERACIONES',
                   'INGRESO', 'DNI', 'NACIMIENTO', 'AFP', 'COMISION', 'CUSPP',
                   'COSTO', 'Báscico', 'TRAB', 'mensual', 'Feriado',
                   'Vacaciones', 'Truncas', 'Gratificaciones', '%', 'NRO', 'IMPORTE',
                   '%', 'NRO', 'IMPORTE', 'CTS', 'Proporcional', 'Proporcional',
                   'MATERNIDAD', 'Familiar', 'AGUINALDOS', 'MOVILIDAD', 'BONIFICACION',
                   'INGRESOS', 'IMPONIBLE', '%', 'IMPORTE', 'CATEG', 'JUDICIAL',
                   'SEGUROS', 'ADELANTOS', 'DESCUENTOS', 'QUINCENA', '%','IMPORTE',
                    '%', 'IMPORTE', '%','IMPORTE','APORTES', 'DESCUNTOS', 'PAGAR',
                    '%', 'IMPORTE', '%', 'IMPORTE', 'PAGAR', 'EPS', 'EPS', 'EPS',
                    'F. INICIO', 'F. TERMINO', 'VACACIONES', '']

        headers22 = ['DIAS', 'HORAS', 'DIAS / HORAS', 'INASISTENCIAS', 'DIAS DE FALTA', '(RD+DD)', '',
                     'DIAS DESCANSO', 'DIAS FERIADOS', 'MOVILIDAD']

        # Company Name
        # sheet.write(0, 0, company.name, format1)
        sheet.merge_range('A2:D2', company.name, format1)
        sheet.write(2, 48, 'TOPE DE PRIMA DE SEGUROS:')  # TOPE DE PRIMA DE SEGUROS
        sheet.write(2, 50,  company.insurance_premium_cap)  # TOPE DE PRIMA DE SEGUROS
        sheet.write(3, 1, 'AÑO:', format2)
        sheet.write(3, 2, data['year'], format2)

        sheet.write(4, 1, 'MES:', format2)
        sheet.write(4, 2, data['month'], format2)

        sheet.write(3, 3, 'DÍAS FERIADOS :', format2)
        sheet.write(3, 4, data['df'], format2)

        sheet.write(4, 3, 'DÍAS DE DESCANSO:', format2)
        sheet.write(4, 4, data['dd'], format2)

        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 30)
        sheet.set_column('D:D', 20)
        sheet.set_column('D:D', 20)
        sheet.set_column('E:E', 10)
        sheet.set_column('F:F', 10)
        sheet.set_column('G:G', 12)
        sheet.set_column('H:H', 10)
        sheet.set_column('H:H', 10)
        sheet.set_column('I:I', 12)
        sheet.set_column('J:J', 10)
        sheet.set_column('K:K', 11)
        sheet.set_column('L:L', 10)
        sheet.set_column('M:M', 10)
        sheet.set_column('N:N', 13)
        sheet.set_column('O:O', 10)
        sheet.set_column('P:P', 10)
        sheet.set_column('Q:Q', 10)
        sheet.set_column('R:R', 13)
        sheet.set_column('S:S', 8)
        sheet.set_column('T:T', 8)
        sheet.set_column('U:U', 8)
        sheet.set_column('V:V', 8)
        sheet.set_column('W:W', 8)
        sheet.set_column('X:X', 8)
        sheet.set_column('Y:Y', 8)
        sheet.set_column('Z:Z', 12)
        sheet.set_column('AA:AA', 12)
        sheet.set_column('AB:AB', 14)
        sheet.set_column('AC:AC', 10)
        sheet.set_column('AD:AD', 12)
        sheet.set_column('AE:AE', 11)
        sheet.set_column('AF:AF', 13)
        sheet.set_column('AG:AG', 10)
        sheet.set_column('AH:AH', 11)
        sheet.set_column('AI:AI', 10)
        sheet.set_column('AJ:AJ', 10)
        sheet.set_column('AK:AK', 10)
        sheet.set_column('AL:AL', 10)
        sheet.set_column('AM:AM', 10)
        sheet.set_column('AN:AN', 11)
        sheet.set_column('AO:AO', 12)
        sheet.set_column('AP:AP', 11)
        sheet.set_column('AQ:AQ', 10)
        sheet.set_column('AR:AR', 10)
        sheet.set_column('AS:AS', 10)
        sheet.set_column('AT:AT', 10)
        sheet.set_column('AU:AU', 10)
        sheet.set_column('AV:AV', 10)
        sheet.set_column('AW:AW', 11)
        sheet.set_column('AX:AX', 12)
        sheet.set_column('AY:AY', 11)
        sheet.set_column('AZ:AZ', 5)
        sheet.set_column('BA:BA', 10)
        sheet.set_column('BB:BB', 5)
        sheet.set_column('BA:BC', 10)
        sheet.set_column('BD:BD', 10)
        sheet.set_column('BE:BE', 8)
        sheet.set_column('BF:BF', 8)
        sheet.set_column('BG:BG', 10)
        sheet.set_column('BH:BH', 10)
        sheet.set_column('BI:BI', 11)
        sheet.set_column('BJ:BJ', 12)
        sheet.set_column('BL:BL', 8)
        sheet.set_column('BM:BM', 8)
        sheet.set_column('BN:BN', 12)
        sheet.set_column('BO:BO', 12)
        sheet.set_column('BP:BP', 14)
        sheet.set_column('BQ:BQ', 14)
        sheet.set_column('BR:BR', 14)
        sheet.set_column('BS:BS', 14)
        sheet.set_column('BT:BT', 14)
        sheet.set_column('BU:BU', 14)

        row = 5
        col = 0
        f2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True,  'fg_color': '#F0AD4E'})
        sheet.merge_range('N5:AH5', 'I      N      G      R      E      S      O      S', f2)
        f3 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'fg_color': '#F00D4E'})
        sheet.merge_range('AI5:AP5', 'D    E    S    C    U    E    N    T    O    S', f3)
        sheet.merge_range('AQ5:AX5', 'A. F. P.', f3)
        f5 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'fg_color': '#F03D4J'})
        sheet.merge_range('AZ5:BD5', 'A  P  O  R  T  A  C  I  O  N  E  S', f5)
        sheet.set_row(5, 16)
        for header in headers1:
            sheet.write(row, col, header, h1)
            col += 1

        for header in headers21:
            sheet.write(row, col, header, h2)
            col += 1

        sheet.merge_range('S6:U6', 'HORAS EXTRAS 25%', h1)
        sheet.merge_range('V6:X6', 'HORAS EXTRAS 35%', h1)
        sheet.merge_range('AI6:AJ6', 'S.N.P.', h1)
        sheet.merge_range('AQ6:AR6', 'APORTE OBLIGAT', h1)
        sheet.merge_range('AS6:AT6', 'COMISION', h1)
        sheet.merge_range('AU6:AV6', 'SEGUROS', h1)
        sheet.merge_range('AZ6:BA6', 'ESSALUD', h1)
        sheet.merge_range('BB6:BC6', 'I.E.S.', h1)
        sheet.merge_range('BH6:BI6', 'V A C A C I O N E S', h1)

        row = 6
        col = 0
        sheet.set_row(6, 12)
        for header in headers2:
            sheet.write(row, col, header, bold)
            col += 1

        for header in headers22:
            sheet.write(row, col, header, h2)
            col += 1

        row = 7
        payslip = self.env['hr.payslip']
        new = workbook.add_format({'fg_color': 'yellow'})
        close = workbook.add_format({'fg_color': '#928e8e'})

        for cont in contracts:
            fstate = None
            is_close = False
            if self.labor_relation_started(cont.date_start, fields.Date.from_string(date_from)):
                fstate = new
            if self.labor_relation_finished(cont.date_end, fields.Date.from_string(date_from)):
                fstate = close
                is_close = True
            sheet.write(row, 0, cont.employee_id.identification_id or '', fstate)
            sheet.write(row, 1, cont.employee_id.name, fstate)
            sheet.write(row, 2, cont.job_id.name, fstate)
            sheet.write(row, 3, cont.employee_id.bank_account_id.acc_number if cont.employee_id.bank_account_id else '')
            sheet.write(row, 4, cont.date_start, fdate)
            sheet.write(row, 5, cont.employee_id.identification_id or '')
            sheet.write(row, 6, cont.employee_id.birthday or '', fdate)
            if cont.employee_id.regimen_pensions == 'onp' or cont.employee_id.regimen_pensions == 'srp':
                if cont.employee_id.regimen_pensions == 'onp':
                    sheet.write(row, 7, cont.employee_id.regimen_pensions.upper())
                else:
                    sheet.write(row, 7, 'SIN REGIMEN')
            else:
                sheet.write(row, 7, cont.employee_id.afp_id.name.upper() if cont.employee_id.afp_id else '')
                sheet.write(row, 8, cont.employee_id.commission_type if cont.employee_id.commission_type else '')
                sheet.write(row, 9, cont.employee_id.CUSPP)
            sheet.write(row, 10, cont.department_id.name)
            domain = [('contract_id', '=', cont.id), ('date_from', '=', date_from),
                      ('credit_note', '=', False),
                      ('refund', '=', False)]
            slip = payslip.search(domain)
            sheet.write(row, 11, slip.normal_wage if slip else 0.0)
            sheet.write(row, 12, slip._get_worked_days_line_number_of_days('WORK100') if slip else 0.0)  # TRABAJADO
            sheet.write(row, 13, slip._get_salary_line_total('BASIC') if slip else 0.0)
            sheet.write(row, 14, slip._get_worked_days_line_amount('LEAVE120') if slip else 0.0)  # FERIADO
            sheet.write(row, 15, slip._get_worked_days_line_amount('VAC') if slip else 0.0)  # VACACIONES
            sheet.write(row, 16, slip._get_salary_line_total('VACTRUN') if slip else 0.0)  # VACACIONES TRUNCAS
            sheet.write(row, 17, slip._get_salary_line_total('BS_GRATIF') if slip else 0.0)  # GRATIFICACIONE
            # horas extras al 25%
            sql = """SELECT cp.employee_id, sum(cp.hours_extra_25) as hours_extra_25, sum(cp.hours_extra_35) as hours_extra_35
                     FROM calendar_operation AS cp
                     WHERE cp.employee_id = %s and "date" >= '%s' and "date" <= '%s' and approve
                     GROUP BY cp.employee_id""" % (cont.employee_id.id, date_from, date_to)
            self._cr.execute(sql)
            result = self._cr.fetchone()

            sheet.write(row, 18, 1.25)  # %
            sheet.write(row, 19, result[1] if result else 0)  # cantidad
            sheet.write(row, 20, slip._get_salary_line_total('OVERTIME-25') if slip else 0.0)  # importe
            # horas extras al 35%
            sheet.write(row, 21, 1.35)  # %
            sheet.write(row, 22, result[2] if result else 0)  # cantidad
            sheet.write(row, 23, slip._get_salary_line_total('OVERTIME-35') if slip else 0.0)  # importe
            # CTS
            cts = 0
            bonus = 0
            grat = 0
            if is_close:
                cts = slip._get_salary_line_total('BS_CTS_TRUNCA')
                bonus = slip._get_salary_line_total('BS_GRATIF_TRUNCA')*0.09
                grat = slip._get_salary_line_total('BS_GRATIF_TRUNCA')
            sheet.write(row, 24, cts)  # cts
            sheet.write(row, 25, grat)  # Gratificación Proporcional
            sheet.write(row, 26, bonus)  # Bonificacción Proporcional

            sheet.write(row, 27, 0.0)  # MATERNIDAD
            sheet.write(row, 28, slip._get_salary_line_total('AF') if slip else 0.0)  # Asignacion familiar
            sheet.write(row, 29, slip._get_salary_line_total('AGUINALDO') if slip else 0.0)  # AGUINALDOS
            sheet.write(row, 30, slip._get_salary_line_total('ST') if slip else 0.0)  # MOVILIDAD
            sheet.write(row, 31, slip._get_salary_line_total('BS_BONO') if slip else 0.0)  # BONIFICACION
            # sheet.write(row, 32, self.get_sum_ingreso(row+1))  # TOTAL INGRESOS
            sheet.write(row, 32, slip._get_salary_line_total('GROSS') if slip else 0.0)  # TOTAL INGRESOS
            # sheet.write(row, 33, self.get_sum_imponible(row+1))  # TOTAL IMPONIBLE
            sheet.write(row, 33, slip._get_salary_line_total('TOTALIMP') if slip else 0.0)  # TOTAL IMPONIBLE
            # S.N.P. cuando es OPN
            onp = False
            if cont.employee_id.regimen_pensions == 'onp':
                onp = company.ofic_norm_prev
            # if self.env.ref('cabalcon_hr.afp_ONP').id == cont.employee_id.afp_id.id:
            #     onp = self.env['res.afp'].browse(cont.employee_id.afp_id.id)

            sheet.write(row, 34, onp if onp else 0)  # %
            sheet.write(row, 35, abs(slip._get_salary_line_total('ONPF')) if slip else 0.0)  # IMPORTE

            sheet.write(row, 36, abs(slip._get_salary_line_total('REN5TA') if slip else 0.0))  # 5TA CATEG
            sheet.write(row, 37, abs(slip._get_salary_line_total('RENJUD') if slip else 0.0))  # RETENCION  JUDICIAL
            sheet.write(row, 38, abs(slip._get_salary_line_total('OTROSEG') if slip else 0.0))  # OTROS SEGUROS
            # sheet.write(row, 39, abs(slip._get_salary_line_total('SAR') if slip else 0.0))  # ADELANTOS
            sheet.write(row, 40, abs(slip._get_salary_line_total('LO') if slip else 0.0))  # OTROS DESCUENTOS
            # sheet.write(row, 41, slip._get_salary_line_total('GROSS') * 0.4 if slip else 0.0)  # PRIMERA QUINCENA
            sheet.write(row, 41, abs(slip._get_salary_line_total('SAR') if slip else 0.0))  # PRIMERA QUINCENA
            #  A. F. P.
            sheet.write(row, 42, cont.employee_id.afp_id.seat if cont.employee_id.afp_id else 0.0)  # % - APORTE OBLIGAT
            sheet.write(row, 43, abs(slip._get_salary_line_total('AFPF')) if slip else 0.0)  # IMPORTE - APORTE OBLIGAT
            commission = 0
            if cont.employee_id.afp_id and cont.employee_id.commission_type == 'FLUJO':
                commission = cont.employee_id.afp_id.commission_flow
                commission_imp = abs(slip._get_salary_line_total('AFPCF'))
                sheet.write(row, 44, commission)  # % - COMISION
                sheet.write(row, 45, commission_imp)  # IMPORTE - COMISION
            elif cont.employee_id.afp_id and cont.employee_id.commission_type == 'MIXTA':
                commission = cont.employee_id.afp_id.commission_mixed
                commission_imp = abs(slip._get_salary_line_total('AFPCM'))
                sheet.write(row, 44, commission)  # % - COMISION
                sheet.write(row, 45, commission_imp)  # IMPORTE - COMISION


            sheet.write(row, 46, cont.employee_id.afp_id.insurance if cont.employee_id.afp_id else 0.0)  # % - SEGURO
            sheet.write(row, 47, abs(slip._get_salary_line_total('AFPS')) if slip else 0.0)  # IMPORTE - SEGURO
            # AR8 + AT8 + AV8
            # sheet.write(row, 48, self.get_sum_aporte(row + 1))  # TOTAL APORTE
            if cont.employee_id.regimen_pensions == 'afp'  and cont.employee_id.afp_code ==  'IN':
                sheet.write(row, 48, abs(slip._get_salary_line_total('TOTALAFPIN')) if slip else 0.0)
            if cont.employee_id.regimen_pensions == 'afp'  and cont.employee_id.afp_code ==  'PR':
                sheet.write(row, 48, abs(slip._get_salary_line_total('TOTALAFPPR')) if slip else 0.0)
            if cont.employee_id.regimen_pensions == 'afp'  and cont.employee_id.afp_code ==  'RI':
                sheet.write(row, 48, abs(slip._get_salary_line_total('TOTALAFPRI')) if slip else 0.0)
            if cont.employee_id.regimen_pensions == 'afp'  and cont.employee_id.afp_code ==  'HA':
                sheet.write(row, 48, abs(slip._get_salary_line_total('TOTALAFPHA')) if slip else 0.0)

            sheet.write(row, 49, self.get_sum_descuento(row+1))  # TOTAL DESCUENTOS
            # sheet.write(row, 50, self.get_sum_neto_a_pagar(row+1))  # NETO A PAGAR 	NET
            sheet.write(row, 50, abs(slip._get_salary_line_total('NET')) if slip else 0.0)  # NETO A PAGAR 	NET
            #  APORTACIONES
            if cont.employee_id.eps:
                essalud_tax = payslip.company_id.eps_tax
            else:
                essalud_tax = payslip.company_id.essalud_tax

            sheet.write(row, 51, essalud_tax)  # % - ESSALUD
            sheet.write(row, 52, slip._get_salary_line_total('ESSALUD') if slip else 0.0)  # IMPORTE - ESSALUD
            # Estas no se usan ya pero se dejaran para mantener las formulas
            sheet.write(row, 53, 0.0)  # % - I.E.S.
            sheet.write(row, 54, 0.0)  # IMPORTE - I.E.S.
            sheet.write(row, 55, self.get_total_aportaciones(row+1))  # TOTAL A APORTAC
            # EPS
            sheet.write(row, 56, slip._get_salary_line_total('EPS') if slip else 0.0)  # EPS
            sheet.write(row, 57, cont.employee_id.eps_credit)  # CREDITO EPS
            sheet.write(row, 58, slip._get_salary_line_total('IMPCRED') if slip else 0.0)  # IMPORTE CREDITO
            # VACACIONES
            vac = self.get_vacations(cont.employee_id.id, date_from, date_to)
            sheet.write(row, 59, vac['date_from'] if vac else '', fdate)  # FECHA DE INICIO
            sheet.write(row, 60, vac['date_to']if vac else '', fdate)  # FECHA DE FIN
            sheet.write(row, 61, vac['days']if vac else 0)  # DIAS DE VAC.

            sheet.write(row, 63, slip._get_worked_days_line_number_of_days('WORK100') if slip else 0.0)  # DIAS
            sheet.write(row, 64, slip._get_worked_days_line_number_of_hours('WORK100') if slip else 0.0)  # HORAS
            sheet.write(row, 65, str(slip._get_worked_days_line_number_of_days('WORK100')) + ' / ' + str(slip._get_worked_days_line_number_of_hours('WORK100')) if slip else 0.0)  # DIAS / HORAS
            sheet.write(row, 66, 0.0)  # INASISTENCIAS
            sheet.write(row, 67, slip._get_worked_days_line_number_of_days('LEAVE90') if slip else 0.0)  # Cantidad de DIAS DE FALTA
            sheet.write(row, 68, self.get_factor_rd_dd(row+1))  # FACTOR DE DESCUENTO
            sheet.write(row, 69, self.get_factor(row+1))  # FACTOR DE DESCUENTO
            sheet.write(row, 70, 0.0)  # DIAS DESCANSO
            sheet.write(row, 71, slip._get_worked_days_line_number_of_days('LEAVE120') if slip else 0.0)  # DIAS FERIADOS
            sheet.write(row, 72, slip._get_salary_line_total('ST') if slip else 0.0)  # MOVILIDAD

            row += 1
        # TOTALES
        init_row = 8
        end_row = row
        ft = workbook.add_format({"bold": True,  'fg_color': '#adb5bd', 'border': 1})
        sheet.write(row, 11, self.get_sum('L', init_row, row), ft)
        sheet.write(row, 13, self.get_sum('N', init_row, row), ft)
        sheet.write(row, 14, self.get_sum('O', init_row, row), ft)  # FERIADO
        sheet.write(row, 15, self.get_sum('P', init_row, row), ft)  # VACACIONES
        sheet.write(row, 16, self.get_sum('Q', init_row, row), ft)  # VACACIONES TRUNCAS
        sheet.write(row, 17, self.get_sum('R', init_row, row), ft)  # GRATIFICACIONE
        # horas extras al 25%
        # sheet.write(row, 18, self.get_sum('S', init_row, row), ft)  # %
        sheet.write(row, 19, self.get_sum('T', init_row, row), ft)  # cantidad
        sheet.write(row, 20, self.get_sum('U', init_row, row), ft)  # importe
        # horas extras al 35%
        # sheet.write(row, 21, self.get_sum('V', init_row, row), ft)  # %
        sheet.write(row, 22, self.get_sum('W', init_row, row), ft)  # cantidad
        sheet.write(row, 23, self.get_sum('X', init_row, row), ft)  # importe
        # CTS
        sheet.write(row, 24, self.get_sum('Y', init_row, row), ft)  # cts
        sheet.write(row, 25, self.get_sum('Z', init_row, row), ft)  # Gratificación Proporcional
        sheet.write(row, 26, self.get_sum('AA', init_row, row), ft)  # Bonificacción Proporcional

        sheet.write(row, 27, self.get_sum('AB', init_row, row), ft)  # MATERNIDAD
        sheet.write(row, 28, self.get_sum('AC', init_row, row), ft)  # Asignacion familiar
        sheet.write(row, 29, self.get_sum('AD', init_row, row), ft)  # AGUINALDOS
        sheet.write(row, 30, self.get_sum('AE', init_row, row), ft)  # MOVILIDAD
        sheet.write(row, 31, self.get_sum('AF', init_row, row), ft)  # BONIFICACION
        sheet.write(row, 32, self.get_sum('AG', init_row, row), ft)  # TOTAL INGRESOS
        sheet.write(row, 33, self.get_sum('AH', init_row, row), ft)  # TOTAL IMPONIBLE
        # S.N.P.
        # sheet.write(row, 34, self.get_sum('AI', init_row, row), ft)  # %
        sheet.write(row, 35, self.get_sum('AJ', init_row, row), ft)  # IMPORTE

        sheet.write(row, 36, self.get_sum('AK', init_row, row), ft)  # 5TA CATEG
        sheet.write(row, 37, self.get_sum('AL', init_row, row), ft)  # RETENCION  JUDICIAL
        sheet.write(row, 38, self.get_sum('AM', init_row, row), ft)  # OTROS SEGUROS
        sheet.write(row, 39, self.get_sum('AN', init_row, row), ft)  # ADELANTOS
        sheet.write(row, 40, self.get_sum('AO', init_row, row), ft)  # OTROS DESCUENTOS
        sheet.write(row, 41, self.get_sum('AP', init_row, row), ft)  # PRIMERA QUINCENA
        #  A. F. P.
        # sheet.write(row, 42, self.get_sum('AQ', init_row, row), ft)  # % - APORTE OBLIGAT
        sheet.write(row, 43, self.get_sum('AR', init_row, row), ft)  # IMPORTE - APORTE OBLIGAT
        # sheet.write(row, 44, self.get_sum('AS', init_row, row), ft)  # % - COMISION
        sheet.write(row, 45, self.get_sum('AT', init_row, row), ft)  # IMPORTE - COMISION
        # sheet.write(row, 46, self.get_sum('AU', init_row, row), ft)  # % - SEGURO
        sheet.write(row, 47, self.get_sum('AV', init_row, row), ft)  # IMPORTE - SEGURO
        sheet.write(row, 48, self.get_sum('AW', init_row, row), ft)  # TOTAL APORTE
        sheet.write(row, 49, self.get_sum('AX', init_row, row), ft)  # TOTAL DESCUENTOS
        sheet.write(row, 50, self.get_sum('AY', init_row, row), ft)  # NETO A PAGAR
        #  APORTACIONES
        # sheet.write(row, 51, self.get_sum('AZ', init_row, row), ft)  # % - ESSALUD
        sheet.write(row, 52, self.get_sum('BA', init_row, row), ft)  # IMPORTE - ESSALUD
        # sheet.write(row, 53, self.get_sum('BB', init_row, row), ft)  # % - I.E.S.
        sheet.write(row, 54, self.get_sum('BC', init_row, row), ft)  # IMPORTE - I.E.S.
        sheet.write(row, 55, self.get_sum('BD', init_row, row), ft)  # TOTAL A PAGAR
        # EPS
        sheet.write(row, 56, self.get_sum('BE', init_row, row), ft)  # EPS
        sheet.write(row, 57, self.get_sum('BF', init_row, row), ft)  # CREDITO EPS
        sheet.write(row, 58, self.get_sum('BG', init_row, row), ft)  # IMPORTE CREDITO
        # VACACIONES
        sheet.write(row, 61, self.get_sum('BJ', init_row, row), ft)  # DIAS DE VAC.

        row = row + 3
        ft2 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True, 'fg_color': '#007bff'})
        sheet.write(row, 1, 'RESUMEN PAGO AFP', ft2)
        sheet.write(row, 2, 'IMPORTE', ft2)
        # AFP
        row += 1
        init_row_ = row
        afps = self.env['res.afp'].search([('code', '!=', 'ONP')])
        for afp in afps:
            sheet.write(row, 1, afp.name.upper())
            sheet.write(row, 2, self.get_sum_afp(row+1, init_row, end_row))
            row += 1

        sheet.write(row, 2, self.get_sum('C', init_row_+1, row))
