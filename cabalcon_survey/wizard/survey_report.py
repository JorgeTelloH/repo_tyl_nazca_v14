from odoo import models
import string


class SurveyReport(models.AbstractModel):
    _name = 'report.cabalcon_survey.survey_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format0 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bold': True, 'color': 'black', 'bottom': True, })
        format1 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color':'#d3dde3', 'color':'black', 'bottom': True, })
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': False})
        fdate = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'num_format': 'dd/mm/yyyy'})
        fdatetime = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'num_format': 'dd/mm/yyyy HH:MM:SS'})
        start_time = data['date']
        end_time = data['date_to']
        # Generate Workbook
        sheet = workbook.add_worksheet(lines.title)
        cols = list(string.ascii_uppercase) + ['AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']
        questions = []
        col_no = 2
        # Fetch available questions
        for item in lines.question_ids:
            row = [None, None, None, None, None]
            row[0] = col_no
            row[1] = item.id
            row[2] = item.title
            col_title = str(cols[col_no]) + ':' + str(cols[col_no])
            row[3] = col_title
            if len(item.title) < 8:
                row[4] = 12
            else:
                row[4] = len(item.title) + 2

            questions.append(row)
            col_no += 1

        # Report Details:
        # List report column headers:
        sheet.write(1, 1, 'Encuesta: ' + lines.title, format0)
        sheet.write(2, 0, 'Número', format1)
        sheet.write(2, 1, 'Usuario', format1)
        for question in questions:
            sheet.write(2, question[0], question[2], format1)

        x = 3
        e_name = 3
        inputs = self.env['survey.user_input'].search([('survey_id', '=', lines.id), ('create_date', '>=', start_time), ('create_date', '<=', end_time)])
        number = 1
        for input in inputs:
            sheet.write(e_name, 0, number, format3)
            sheet.write(e_name, 1, input.partner_id.name, format3)
            lines = self.env['survey.user_input.line'].search([('user_input_id', '=', input.id)])
            for line in lines:
                for question in questions:
                    if line.question_id.id == question[1]:
                        value = ''
                        format = format3
                        if line.question_id.question_type == 'date':
                            value = line.value_date
                            format = fdate
                        elif line.question_id.question_type == 'datetime':
                            value = line.value_datetime
                            format = fdatetime
                        elif line.question_id.question_type == 'numerical_box':
                            value = line.value_numerical_box
                        elif line.question_id.question_type == 'text_box':
                            value = line.value_text_box
                        elif line.question_id.question_type == 'char_box':
                            value = line.value_char_box
                        elif line.question_id.question_type == 'simple_choice':
                            value = line.question_id.suggested_answer_ids.filtered(lambda an: an.id == line.suggested_answer_id.id).value
                        elif line.question_id.question_type == 'multiple_choice':
                            answers = lines.filtered(lambda an: an.question_id.id == line.question_id.id).mapped("suggested_answer_id").ids
                            values = line.question_id.suggested_answer_ids.filtered(lambda an: an.id in answers).mapped('value')
                            value = ','.join(values)
                        else:
                            value = ''

                        sheet.write(x, question[0], value, format)
            x += 1
            e_name += 1
            number += 1

        # set width and height of colmns & rows:
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 35)
        for question in questions:
            sheet.set_column(question[3], question[4])
        sheet.set_column('C:C', 20)


