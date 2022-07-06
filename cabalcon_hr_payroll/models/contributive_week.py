from datetime import datetime
from odoo import fields, models, api


class ContributiveWeek(models.Model):
    _name = 'contributive.week'
    _description = 'Semanas contributivas'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(2022, datetime.now().year + 10, 1)]

    name = fields.Char(string='Nombre')
    week = fields.Integer(string='# Semana', required=True)
    name = fields.Char(string='Nombre')
    year_week = fields.Selection(string='Año', selection=_get_years, required=True)
    week_from = fields.Date(string='Desde', required=True)
    week_to = fields.Date(string='Hasta', required=True)

    @api.model
    def create(self, values):
        name = "Semana {} de {}".format(values['week'], values['year_week'])
        values['name'] = name
        return super(ContributiveWeek, self).create(values)

    _sql_constraints = [('contributive_week_uniq', 'unique (week, year_week)',
                         'Duplicando semana contributivas!')]
