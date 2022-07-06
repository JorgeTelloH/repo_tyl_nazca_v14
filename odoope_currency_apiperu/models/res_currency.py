# -*- coding: utf-8 -*-
import json
import time
import requests

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    @api.model
    def create(self, vals):
        # OVERRIDE
        if vals.get('rate') and not vals.get('rate_pe'):
            if vals.get('rate') == 1:
                vals['rate_pe'] = 1
            else:
                vals['rate_pe'] = 1/vals.get('rate')
        result = super(CurrencyRate, self).create(vals)
        return result


    def write(self, vals):
        if vals.get('rate') and not vals.get('rate_pe'):
            if vals.get('rate') == 1:
                vals['rate_pe'] = 1
            else:
                vals['rate_pe'] = 1 / vals.get('rate')
        res = super(CurrencyRate, self).write(vals)
        return res

