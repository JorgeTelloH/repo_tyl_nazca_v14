# -*- coding: utf-8 -*-

from odoo import fields, models

ONE = '1'
EIGTH = '8'
NINE = '9'
STATE_SUNAT_SELECTION = [(ONE, '1'), (EIGTH, '8'), (NINE, '9')]

TYPE_A = 'A'
TYPE_M = 'M'
TYPE_C = 'C'
TYPE_SUNAT_SELECTION =[(TYPE_A, 'Apertura del Ejercicio'), (TYPE_M, 'Movimiento del mes'), (TYPE_C, 'Cierre del Ejercicio')]

BALANCE = 'balance'
LOSS_GAIN = 'loss_gain'
TYPE_PLAN_SELECTION = [(BALANCE, 'Cuentas del Balance General'), (LOSS_GAIN, 'Cuentas de ganancia y pérdidas')]


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_pe_operation_state_sunat = fields.Selection(selection=STATE_SUNAT_SELECTION, string='Estado de Operación SUNAT', default=ONE)
    l10n_pe_operation_type_sunat = fields.Selection(selection=TYPE_SUNAT_SELECTION, string='Tipo de Operación SUNAT', default=TYPE_M)

class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    l10n_pe_type_plan = fields.Selection(selection=TYPE_PLAN_SELECTION, string='Tipo según Plan Contable', default=BALANCE)

# class AccountJournal(models.Model):
#     _inherit = 'account.journal'
#
#     enable_report_ple_sales = fields.Boolean(string="Activar Reporte PLE Ventas",
#         help="Activar Reporte PLE Ventas para la SUNAT")
#     enable_report_ple_purchases = fields.Boolean(string="Activar Reporte PLE Compras",
#         help="Activar Reporte PLE Compras para la SUNAT")
