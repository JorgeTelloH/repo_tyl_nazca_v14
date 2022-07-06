# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

semana = [
    ('0', 'Lunes'),
    ('1', 'Martes'),
    ('2', 'Miércoles'),
    ('3', 'Jueves'),
    ('4', 'Viernes'),
    ('5', 'Sábado'),
    ('6', 'Domingo')
]


class OperationSchedule(models.Model):
    _inherit = 'operations.schedule'

    roll_id = fields.Many2one('operations.roll', string='Roll', required=False)

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        if self.date_from and self.date_to:
            if self.date_from >= self.date_to:
                raise ValidationError(_('La fecha final no puede ser mayor a la fecha inicial'))
            else:
                lines = []
                i = 0
                days = 1
                calculate_date = self.date_from
                while i < 1:
                    week = calculate_date.isoweekday() - 1
                    months = (
                        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
                        "Octubre",
                        "Noviembre", "Diciembre")
                    month = months[calculate_date.month - 1]
                    long_date = "{} de {} del {}".format(calculate_date.day, month, calculate_date.year)
                    name = semana[week][1] + " " + long_date + " " + "09:00 a 18:00"
                    lines.append((0, 0, {'name': name, 'dayofweek': str(week), 'hour_from': 9, 'hour_to': 18,
                                         'date': calculate_date}))
                    calculate_date = calculate_date + datetime.timedelta(days=1)
                    if calculate_date > self.date_to:
                        break
                if lines:
                    self.lines_ids = [(5, 0, 0)] + lines


