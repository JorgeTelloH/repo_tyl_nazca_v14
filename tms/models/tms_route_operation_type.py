# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TmsRouteServiceType(models.Model):
    _name = 'tms.route.operation.type'
    #_inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Tipo de Operacion TMS'
    _order = "name"

    name = fields.Char(string='Tipo de Operación TMS', required=True)
    vendor_required = fields.Boolean(string="Requerir Proveedor", default=True, help='Activar solo si requiere el Proveedor en la Operación TMS.')
    tracking_required = fields.Boolean(string="Requerir Tracking", default=True, help='Activar solo si requiere Seguimiento de la Operación TMS.')
    active = fields.Boolean(string="Activo", default=True, index=True)
    vehicle_required = fields.Boolean(string="Requerir Vehículo", help='Activar solo si requiere el Vehículo en la Operación TMS.')
    guide_required = fields.Boolean(string="Requerir Guías", help='Activar solo si requiere registar Guias en la Operación TMS.')
    able_advance = fields.Boolean(string="Permitir Adelanto?", default=False)
    percent_advance = fields.Float(string="Porcentaje de Adelanto", 
        help="Indicar el porcentaje de adelanto por Tipo de Operación", default=0)

    _sql_constraints = [ ('001_name', 'unique(name)', 'Tipo de Operación ya existe!') ]


    @api.onchange('able_advance')
    def _onchange_able_advance(self):
        if self.able_advance == False:
            self.percent_advance = 0.00
