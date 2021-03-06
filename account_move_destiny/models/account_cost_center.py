# -*- coding: utf-8 -*-

import time
import math

from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class AccountCostCenter(models.Model):
    _inherit = 'account.cost.center'

    target_debit_id = fields.Many2one('account.account', string='Cuenta de amarre al Debe')
    target_credit_id = fields.Many2one('account.account', string='Cuenta de amarre al Haber')