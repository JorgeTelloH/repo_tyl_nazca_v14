# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_unit_hist = fields.Float(string='Precio unitario histórico', digits='Product Price', default=0.0, readonly=True)

    @api.onchange('product_id')
    def _price_hist_onchange(self):
        for rec in self:
            if rec.product_id:
                if self.order_id.pricelist_id and self.order_id.partner_id:
                    product = rec.product_id.with_context(
                        lang=rec.order_id.partner_id.lang,
                        partner=rec.order_id.partner_id,
                        quantity=rec.product_uom_qty,
                        date=rec.order_id.date_order,
                        pricelist=rec.order_id.pricelist_id.id,
                        uom=rec.product_uom.id,
                        fiscal_position=rec.env.context.get('fiscal_position')
                    )
                    rec.price_unit_hist = rec.env['account.tax']._fix_tax_included_price_company(rec._get_display_price(product), product.taxes_id, rec.tax_id, rec.company_id)
                else:
                    rec.price_unit_hist = rec.product_id.standard_price
