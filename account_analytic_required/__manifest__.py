# -*- coding: utf-8 -*-
{
    'name': 'Cuenta Analitica requerida',
    'summary': """
        Activar Cuenta Analitica como requerida""",
    'description': """
        Permite seleccionar el tipo de política requerido para validar la Cuenta Analitica.\n
        Configuración:\n
        Ir a Ajustes / Contabilidad / Sección Analítica: Cuenta Analítica requerida.\n
        Uso:\n
        Validación de Cuenta Analítica en Comprobantes y Asientos Contables.
    """,
    
    'author': 'TH',
    'website': "http://www.cabalcon.com",
    'category': 'Accounting',
    'version': '1.1',
    
    # any module necessary for this one to work correctly
    'depends': ['account', 'account_accountant',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False
}
