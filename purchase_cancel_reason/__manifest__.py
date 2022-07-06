# -*- coding: utf-8 -*-
{
    "name": "Razón de Cancelación de Orden de Compra",

    'summary': """
        Razones de Cancelación de Orden de Compra""",

    'description': """
        Razones de Cancelación de Orden de Compra.
    """,

    "version": "14.0.1.0.0",
    "author": "TH",
    "category": "Purchase",
    "website": "www.cabalcon.com",

    "depends": ["purchase"],
    "data": [
        "wizard/purchase_cancel_reason_view.xml",
        "views/purchase_order.xml",
        "security/ir.model.access.csv",
        "data/purchase_order_cancel_reason.xml",
    ],
    "auto_install": False,
    "installable": True,
}
