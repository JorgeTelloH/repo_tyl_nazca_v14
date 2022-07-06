# -*- coding: utf-8 -*-
{
    'name': "SuperTool Technologies",

    'summary': """
        SuperTool Technologies""",

    'description': """
    	SuperTool Technologies.\n
    	Instalacion:\n
    	Ir a Proyectos / Configuración ==> Activar Registros de Tareas y Subtarea.
    """,

    'author': "Cabalcon",
    'website': "http://www.cabalcon.com",

    'category': 'SuperTool Technologies',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['mail', 'calendar', 'crm', 'project', 'board', 'project_extended'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/supertool_view.xml',
    ],
}
