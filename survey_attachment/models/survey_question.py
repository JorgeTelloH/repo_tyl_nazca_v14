# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
import base64
import json
from odoo.tools import date_utils
import os
import re


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_attachment = fields.Binary('Question attachment')
    question_type = fields.Selection(selection_add=[
        ('upload_file', 'Upload file')
    ])


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    # def save_lines(self, question, answer, comment=None):
    #     res = super(SurveyUserInput, self).save_lines(question, answer, comment=None)
    #     old_answers = self.env['survey.user_input.line'].search([
    #         ('user_input_id', '=', self.id),
    #         ('question_id', '=', question.id),
    #         ('answer_type', '=', question.question_type)
    #     ])
    #     if question.question_type == 'upload_file':
    #         self.save_upload_file(question, old_answers, answer)
    #     return res

    def save_lines(self, question, answer, comment=None):
        """ Save answers to questions, depending on question type

            If an answer already exists for question and user_input_id, it will be
            overwritten (or deleted for 'choice' questions) (in order to maintain data consistency).
        """
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])

        if question.question_type in ['char_box', 'text_box', 'numerical_box', 'date', 'datetime']:
            self._save_line_simple_answer(question, old_answers, answer)
            if question.save_as_email and answer:
                self.write({'email': answer})
            if question.save_as_nickname and answer:
                self.write({'nickname': answer})

        elif question.question_type in ['simple_choice', 'multiple_choice']:
            self._save_line_choice(question, old_answers, answer, comment)
        elif question.question_type == 'matrix':
            self._save_line_matrix(question, old_answers, answer, comment)
        if question.question_type == 'upload_file':
            self.save_upload_file(question, old_answers, answer)
        #else:
            #raise AttributeError(question.question_type + ": This type of question has no saving function")

    def save_upload_file(self, question, old_answers, answer):
        vals = self._get_line_upload_file_values(question, answer, 'upload_file')
        if old_answers:
            old_answers.write(vals)
            return old_answers
        else:
            return self.env['survey.user_input.line'].create(vals)
        return True

    def _get_line_upload_file_values(self, question, answer, answer_type):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': answer_type,
        }
        if not answer or (isinstance(answer, str) and not answer.strip()):
            vals.update(answer_type=None, skipped=True)
            return vals

        f = answer.split(",")
        b = re.split(',|:|\/', f[0])
        if b[1] == 'image':
            itemtype = 'image'
        else:
            itemtype = 'pdf'
        file1 = f[1].encode(encoding='UTF-8')
        file_name = f[2].strip('"')
        if answer_type == 'upload_file':
            vals['name_file'] = file_name
            vals['value_upload_file'] = file1
            vals['file_type'] = itemtype
        return vals


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    answer_type = fields.Selection(selection_add=[
        ('upload_file', 'Upload file')
    ])

    value_upload_file = fields.Binary('Upload file')
    name_file = fields.Char('Name file')
    file_type = fields.Selection([('image', 'image'), ('pdf', 'pdf')])


