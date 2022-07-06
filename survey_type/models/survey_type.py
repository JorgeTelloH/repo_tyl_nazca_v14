# -*- coding: utf-8 -*-
import calendar
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _

class SurveyType(models.Model):
    _name = 'survey.type'
    _description = "Survey Type"

    name = fields.Char(string='Survey Type')
    active = fields.Boolean(string='Active')