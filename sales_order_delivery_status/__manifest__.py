# -*- coding: utf-8 -*-
{
	'name': 'Estado de Entrega en Pedido de Venta',
    'summary': 'Agregar Estado de Entrega en Pedido de Venta',
    'description': """
        Agregar Estado de Entrega en Pedido de Venta
    """,
	
    'author': 'TH',
    'website': 'http://www.cabalcon.com',
    
    'category': 'Sales',
    'version': '1.1',
	
    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'sale_stock'],
	
	# always loaded
    'data': [
    	'views/sales_order.xml'
    ],

}
