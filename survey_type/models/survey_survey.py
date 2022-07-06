# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SurverySuveryInherit(models.Model):
    _inherit = 'survey.survey'

    survey_type_id = fields.Many2one(
        'survey.type', string="Tipo de Encuesta",domain="[('active', '=', True)]")