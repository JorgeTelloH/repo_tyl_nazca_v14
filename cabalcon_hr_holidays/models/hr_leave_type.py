# -*- coding: utf-8 -*-

import datetime
import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    def unlink(self):
        for type in self:
            if type.id == self.env.ref('cabalcon_hr_holidays.holiday_status_vac').id:
                raise ValidationError('El registro no se puede eliminar porque está siendo usado por el sistema')
            if type.id == self.env.ref('hr_holidays.holiday_status_sl').id:
                raise ValidationError('El registro no se puede eliminar porque está siendo usado por el sistema')
            return super(HolidaysType, self).unlink()
