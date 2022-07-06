# -*- coding: utf-8 -*-

from collections import defaultdict
import datetime
from odoo import api, fields, models, tools, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    plan_ini_date = fields.Date(string='Fecha Inicio')
    plan_fin_date = fields.Date(string='Fecha Fin')
    real_ini_date = fields.Date(compute="compute_real_date", string='Inicio Real', store=True, 
        help='Fecha de Inicio Real calculado desde Partes de Horas registrado por el usuario')
    real_fin_date = fields.Date(compute="compute_real_date", string='Fin Real', store=True,
        help='Fecha de Fin Real calculado desde Partes de Horas registrado por el usuario')
    level = fields.Selection([
        ('alta', 'Alta'),
        ('media', 'Media'), 
        ('baja', 'Baja')], 
        string='Prioridad', copy=False, default='baja')
    task_type = fields.Selection([
        ('support', 'Soporte'), 
        ('incidence', 'Incidencia'), 
        ('close_stage', 'Cierre 1er Pase'),
        ('close_pass', 'Cierre 2do Pase'),
        ('close_project', 'Cierre de Proyecto'),
        ('requirement', 'Requerimiento')], 
        string='Tipo de Tarea', copy=False)
    assigned_area = fields.Char(string='Area')

    @api.depends('timesheet_ids')
    def compute_real_date(self):
        for rec in self:
            if rec.timesheet_ids:
                list_times = []
                for time_sheet in rec.timesheet_ids:
                    list_times.append(time_sheet.date)
                if list_times:
                    rec.real_ini_date = min(list_times)
                    rec.real_fin_date = max(list_times)
            else:
                if rec.real_ini_date or rec.real_fin_date:
                    rec.real_ini_date = False
                    rec.real_fin_date = False
