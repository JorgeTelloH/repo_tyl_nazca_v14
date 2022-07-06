# -*- coding: utf-8 -*-
{
    "name": "Bloquear Envio de Email de Socio",
    "summary": """
    	Bloquear el envio de email en Partner""",
    'description': """
        Aplicar Bloqueo de envio de email en Partner.\n
        Uso:\n
        Ir al modulo de Partner: En el campo de email del Socio se verá un botón para activar/desactivar el bloqueo de envio de email.
    """,

    "author": "TH",
    'category': 'Hidden/Tools',
    'version': '1.1',
    "website": "www.cabalcon.com",
    "data": [
    	"views/res_partner_views.xml"
    	],
    "depends": ["mail"],
    
    "installable": True,
}
