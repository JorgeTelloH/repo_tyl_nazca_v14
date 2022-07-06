# -*- coding: utf-8 -*-
{
    'name': "Acceso de solo lectura para Usuario",

    'summary': """
        Acceso de solo lectura para usuario específico""",

    'description': """
        Permite el acceso de usuario especifico a modo de solo lectura en Sistema.
        Configuración:\n
        Ir a Ajustes / Usuarios: Activar el botón de Acceso de Solo lectura.\n
        Uso:\n
        Al acceder a cualquier modulo, el usuario solo estará limitado a Modo Lectura.
    """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Extra Tools',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/user_read_only_group.xml',
        'security/ir.model.access.csv',
        'views/res_users.xml',
    ],
}