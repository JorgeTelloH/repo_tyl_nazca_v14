# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ErrorImportVacations(models.Model):
    _name = "hr_import_vacations.error"
    _description = "Módelo para mostrar los errore en la importación de asignación de vacaciones"

    ci = fields.Char(string='DNI')
    error = fields.Char(string='Error')


