# -*- coding: utf-8 -*-

import datetime
import dateutil.relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError

_STATES_READONLY = {'validated': [('readonly', True)], 'declared': [('readonly', True)]}

DRAFT = 'draft'
VALIDATED = 'validated'
DECLARED = 'declared'
STATE_SELECTION = [(DRAFT, 'Borrador'), (VALIDATED, 'Validado'), (DECLARED, 'Declarado')]

CLOSE_OPERATION = '0'
FACTORY = '1'
CLOSED = '2'
OPERATION_INDICATOR_SELECTION = [
    (CLOSE_OPERATION, 'Cierre de Operaciones - baja de inscripción RUC'),
    (FACTORY, 'Empresa o Entidad operativa'),
    (CLOSED, 'Cierre del Libro')
    ]

WITH_INFO = '1'
WITHOUT_INFO = '0'
INDICATOR_CONTENT_SELECTION = [(WITH_INFO, 'Con información'), (WITHOUT_INFO, 'Sin información')]

NORMAL = 'normal'
SIMPLIFIED = 'simplified'
TYPE_REPORT_SELECTION = [(NORMAL, 'Normal'), (SIMPLIFIED, 'Simplificado')]


class ReportPle(models.Model):
    _name = 'report.ple'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'report.report_xlsx.abstract']
    _description = 'Reporte PLE'
    _order = "name desc"

    name = fields.Char(string='Nombre', states=_STATES_READONLY)
    file_txt = fields.Binary(string='Archivo TXT', readonly=True)
    filename_txt = fields.Char(string='Nombre del archivo TXT')
    code = fields.Char(string='Código', readonly=True, states=_STATES_READONLY)
    state = fields.Selection(selection=STATE_SELECTION, string='Estado', default=DRAFT)
    #range_id = fields.Many2one(comodel_name='account.period', string='Periodo', required=True, states=_STATES_READONLY)
    date_from = fields.Date(string='Fecha Desde', required=True)
    date_to = fields.Date(string='Fecha Hasta', compute="_compute_date", store=True)
    period_special = fields.Boolean(string='Apertura/Cierre', states=_STATES_READONLY)
    file_simplified = fields.Binary(string='Archivo TXT simplificado', readonly=True)
    indicator_operation = fields.Selection(selection=OPERATION_INDICATOR_SELECTION, string='Indicador de operaciones',
                                           default=FACTORY, required=True, 
                                           states=_STATES_READONLY)
    indicator_content = fields.Selection(selection=INDICATOR_CONTENT_SELECTION, string='Indicador del contenido',
                                         default=WITH_INFO, required=True, 
                                         states=_STATES_READONLY)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Moneda', domain=[('name', 'in', ['PEN', 'USD'])],
                                  default=lambda self: self.env.user.company_id.currency_id, required=True,
                                  states=_STATES_READONLY)
    company_id = fields.Many2one(comodel_name='res.company', string='Empresa',
                                 default=lambda self: self.env.user.company_id, required=True, states=_STATES_READONLY)
    type_report = fields.Selection(selection=TYPE_REPORT_SELECTION, string='Tipo de reporte', default=NORMAL,
                                   states=_STATES_READONLY)

    @api.depends("date_from")
    def _compute_date(self):
        if self.date_from:
            fir_date = self.date_from.replace(day=1)
            d2 = fir_date + dateutil.relativedelta.relativedelta(months=1)
            last_day = d2 - dateutil.relativedelta.relativedelta(days=1)
            self.date_to = last_day
        else:
            self.date_to = False
        return

    def action_generate_ple(self, value):
        value.update({'state': 'validated'})
        self.write(value)

    def action_declare(self):
        self.write({'state': 'declared'})

    @api.model
    def get_year_month(self, date):
        from_date = fields.Date().from_string(date)
        #return '{}{}'.format(from_date.year, from_date.month) if date else ''
        return '{}{}'.format(from_date.year, from_date.rjust(2, "0")) if date else ''
