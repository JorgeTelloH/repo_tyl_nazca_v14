# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrderCancel(models.TransientModel):
    _name = "purchase.order.cancel"

    reason_id = fields.Many2one(comodel_name="purchase.order.cancel.reason", string="Razón", required=True)

    def confirm_cancel(self):
        self.ensure_one()
        act_close = {"type": "ir.actions.act_window_close"}
        purchase_ids = self._context.get("active_ids")
        if purchase_ids is None:
            return act_close
        assert len(purchase_ids) == 1, "Solo 01 Orden de Compra"
        purchase = self.env["purchase.order"].browse(purchase_ids)
        purchase.cancel_reason_id = self.reason_id.id
        purchase.button_cancel()
        return act_close
