# -*- coding: utf-8 -*-

import logging

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    valid_period_from = fields.Datetime('Start period', index=True, copy=False, default=fields.Date.context_today,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, tracking=True)
    valid_period_to = fields.Datetime('End period',  copy=False, tracking=True,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)], 'validate': [('readonly', True)]})
    is_vacation = fields.Boolean(string='Es una asignación de vacaciones', compute='_compute_is_vacation')

    @api.onchange('valid_period_from')
    def onchange_valid_period_from(self):
        if self.valid_period_from:
            self.valid_period_to = self.valid_period_from + relativedelta(years=1)

    @api.depends('holiday_status_id')
    def _compute_is_vacation(self):
        for allocation in self:
            allocation.is_vacation = (allocation.holiday_status_id == self.env.ref('cabalcon_hr_holidays.holiday_status_vac'))

    @api.constrains("valid_period_from", "valid_period_to")
    def _check_dates(self):
        for record in self:
            if (record.valid_period_from and record.valid_period_to and record.valid_period_from > record.valid_period_to):
                raise ValidationError("La fecha de inicio no puede ser mayor que la fecha fin.")




