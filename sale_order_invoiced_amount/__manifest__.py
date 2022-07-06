# -*- coding: utf-8 -*-
{
    "name": "Monto Facturado en Pedido de Venta",
    "summary": "Mostrar monto Factura en Pedido de Venta",
    'description': """
        Mostrar monto Factura en Pedido de Venta
    """,
    
    "author": "TH",
    "category": "Sales",
    "version": "1.1",
    # any module necessary for this one to work correctly
    "depends": ["sale"],
    "data": [
    	"views/sale_order_view.xml"
    	],
    "installable": True,
}
