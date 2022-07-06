# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#Estados del Account Invoice
AI_STATES = [('draft','Borrador'),('open','Emitido'),('paid','Pagado'),('cancel','Anulado')]
#Tipos del Account Invoice
AI_TYPE = [('out_invoice','Documento Cliente'),('in_invoice','Documento Proveedor'),('out_refund','NC Cliente'),('in_refund','NC Proveedor'),('entry', 'Asiento Diario')]

class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    route_operation_id = fields.Many2one('tms.route.operation', string='Operación', index=True)
    operation_type_id = fields.Many2one(related="route_operation_id.operation_type", string='Tipo Operación', readonly=True, store=True)
    invoice_state = fields.Selection(AI_STATES, readonly=True, String='Estado', index=True, related="move_id.state", store=True)
    invoice_reference = fields.Char(related="move_id.ref", string='Doc Proveedor', readonly=True, store=True)
    invoice_type = fields.Selection(AI_TYPE, readonly=True, String='Tipo', index=True, related="move_id.move_type", store=True)

    @api.onchange('route_operation_id')
    def _onchange_operation_id(self):
        if self.route_operation_id:
            #Validamos que tenga proveedor la Operacion, caso contrario se pueda imputar a otros proveedores
            if self.route_operation_id.vendor_id.id:
                #Validamos que el proveedor de la Factura corresponde con el Proveedor de la Operacion
                if self.route_operation_id.vendor_id != self.invoice_id.partner_id:
                    raise ValidationError(
                    _("La Operación: %s \n No corresponde al Proveedor: %s \n Su proveedor de Operación es: %s") % (
                        self.route_operation_id.name, self.invoice_id.partner_id.name, self.route_operation_id.vendor_id.name))

            self.product_id = self.route_operation_id.product_id
            self.quantity = self.route_operation_id.product_qty
            self.price_unit = self.route_operation_id.cost_ppto_unit
        else:
            if not self.route_operation_id:
                self.quantity = 1
                self.price_unit = 0