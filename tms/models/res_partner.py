# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    operation_type_id = fields.Many2many('tms.route.operation.type', 'res_partner_operation_type_rel', 'partner_id', 'operation_type_id', string="Tipo de Operación")
    active_platform_gps = fields.Boolean(string='Activar Plataforma GPS', help='Activar si es Proveedor de Flete')
    platform_gps_ids = fields.One2many('res.partner.platform.gps', 'partner_id')
    operation_type_domain = fields.Text(string='Dominio de Tipo de Operación', compute='_get_oper_type_domain', store=True, index=True)
    partner_alert_ids = fields.One2many('res.partner.alerts', 'partner_id')
    tms_expense_account_id = fields.Many2one('account.account', string='Cuenta de Gasto TMS', 
        help='Cuenta de Gastos TMS que puede ser usada por defecto en los Pagos de Adelanto.')
    vendor_alert = fields.Boolean(compute='_activate_alert', string='Activar Alerta Factura', store=True, default=False)
    vendor_alert_msg = fields.Text(compute='_activate_alert', string="Mensaje de Alerta proveedor", store=True)


    @api.depends('operation_type_id')
    def _get_oper_type_domain(self):
        v_cadena = ''
        v_activar = False
        for operation in self.operation_type_id:
            v_cadena = v_cadena + str(operation.id) + ','
        self.operation_type_domain = v_cadena

    #activar / desactivar alerta de proveedor para comprobante de proveedor
    @api.depends('partner_alert_ids', 'partner_alert_ids.alert_active')
    def _activate_alert(self):
        #Obtener el monto imputado en Invoices
        for rec in self:
            #tiene registro de alerta
            v_msg = ''
            if rec.partner_alert_ids:
                for line in rec.partner_alert_ids:
                    if line.group_alert == 'invoice' and line.alert_active == 'activo' :
                        v_msg = v_msg + line.message + "\n"
                if len(v_msg) > 1:
                    rec.vendor_alert = True
                    rec.vendor_alert_msg = v_msg
                else:
                    if rec.vendor_alert == True:
                        rec.vendor_alert = False
                        rec.vendor_alert_msg = v_msg
            else:
                if rec.vendor_alert == True:
                    rec.vendor_alert = False
                    rec.vendor_alert_msg = v_msg
