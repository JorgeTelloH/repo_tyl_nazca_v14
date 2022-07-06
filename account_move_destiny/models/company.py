# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import calendar
import time
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_round, float_is_zero


class ResCompany(models.Model):
    _inherit = "res.company"

    automatic_destiny = fields.Boolean(string='Destinos automaticos', default=False)
    # priorise_destiny = fields.Selection([('analitic', "Cuenta analitica"), ('cost_center', "Centro de costo")], string='Priorizar destino')