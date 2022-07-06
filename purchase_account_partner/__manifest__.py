# -*- coding: utf-8 -*-
{
    'name': "Pasar Cuenta Contable desde Orden de Compra a la Factura",

    'summary': """
        Asignar Cuenta Contable del proveedor desde la Orden de Compra a la Factura""",

    'description': """
        Asignar Cuenta Contable por pagar del proveedor desde la Orden de Compra a la Factura
    """,

    'author': "Oswaldo Lopez (Cabalcon)",

    'category': 'Inventory/Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
}
