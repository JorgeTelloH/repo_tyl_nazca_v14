# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Contract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def create(self, vals):
        res = super(Contract, self).create(vals)
        validity_start = datetime.combine(res.date_start, datetime.min.time())
        validity_start = validity_start.replace(year=datetime.now().year)
        if res.date_start.month < datetime.now().month:
            validity_stop = validity_start + relativedelta(years=1)
        else:
            validity_stop = validity_start
            validity_start = validity_start - relativedelta(years=1)

        res.employee_id.write({'validity_start': validity_start,
                               'validity_stop': validity_stop})
        return res

    def write(self, vals):
        res = super(Contract, self).write(vals)
        if 'date_start' in vals:
            validity_start = datetime.combine(self.date_start, datetime.min.time())
            validity_start = validity_start.replace(year=datetime.now().year)
            validity_stop = validity_start + relativedelta(years=1)

            self.mapped('employee_id').write({'validity_start': validity_start,
                                              'validity_stop': validity_stop})
        return res

