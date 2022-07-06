# -*- coding: utf-8 -*-
{
	'name': "Ocultar Costo y Precio del Producto",
    'summary': """
        Ocultar Costo y Precio del Producto""",
    'description': """
        Ocultar Costo y Precio del Producto.\n
        Configuración:\n
        Ir a Ajustes / Usuarios y Compañías / Usuarios ==> Activar las opciones:\n
        - Mostrar Precio de Producto.\n
        - Mostrar Costo de Producto.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",
    
    'category': 'Sales',
    'version': '1.1',
    
    # any module necessary for this one to work correctly
    'depends': ['sale_management','product'],

	# always loaded
    'data': [
    	'security/show_cost_price_product.xml',
    	'views/product_cost_price_view.xml',
    ],
}
