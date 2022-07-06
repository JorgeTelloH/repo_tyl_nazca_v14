# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError


class SurveyCategory(models.Model):
    _name = 'survey.category'
    _description = 'Survey Category'

    name = fields.Char('Nombre', required=True)


class Survey(models.Model):
    _inherit = 'survey.survey'

    category_id = fields.Many2one('survey.category', string='Categoría')
 