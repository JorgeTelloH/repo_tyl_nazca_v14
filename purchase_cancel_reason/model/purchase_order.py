# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    cancel_reason_id = fields.Many2one(comodel_name="purchase.order.cancel.reason", string="Razón de Cancelación",
        readonly=True, ondelete="restrict")


class PurchaseOrderCancelReason(models.Model):
    _name = "purchase.order.cancel.reason"
    _description = "Razón de Cancelación de Orden de Compra"

    name = fields.Char(string="Razón", required=True)
    sequence = fields.Integer(string='secuencia', default=99)
    active = fields.Boolean(string="Activo", default=True)
