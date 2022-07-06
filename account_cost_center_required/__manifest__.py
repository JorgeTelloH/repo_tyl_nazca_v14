# -*- coding: utf-8 -*-
{
    'name': 'Centro de Costo requerido',
    'summary': """
        Activar Centro de Costo como requerido""",
    'description': """
        Permite seleccionar el tipo de política requerido para validar el Centro de Costo.\n
        Configuración:\n
        Ir a Ajustes / Contabilidad / Sección Centro de Costo:  Centro de Costo requerido.\n
        - Opcion: 'Nunca'           ==> No valida el Centro de Costo (Por defecto).\n
        - Opcion: 'Siempre'         ==> Valida el Centro de Costo al Grabar y Publicar.\n
        - Opcion: 'Solo Publicados' ==> Valida el Centro de Costo al Publicar.\n
        Uso:\n
        Validación de Centro de Costo en Comprobantes y Asientos Contables.
    """,
    
    'author': 'TH',
    'website': "http://www.cabalcon.com",
    'category': 'Accounting',
    'version': '1.1',
    
    # any module necessary for this one to work correctly
    'depends': ['account', 'account_accountant', 'account_cost_center',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
