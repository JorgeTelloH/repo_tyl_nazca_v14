# -*- coding: utf-8 -*-
{
    "name": "Tipo de Orden de Compra",
    "summary": "Agrega un Tipo configurable en la Orden de Compra.",
    'description' : """
        Agrega un tipo configurable en las Ordenes de compra. Este tipo se puede utilizar en filtros y grupos.\n
        Configuración:\n
        - Ir a Compras / Configuración / Tipos de compra.
        """,
    "author": "TH",
    "website": "http://www.cabalcon.com",

    'category' : "Inventory/Purchase",
    "version": "1.1",
    
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/view_purchase_order_type.xml",
        "views/view_purchase_order.xml",
        "views/res_partner_view.xml",
        "data/purchase_order_type.xml",
    ],
    "installable": True,
    "auto_install": False,
}
