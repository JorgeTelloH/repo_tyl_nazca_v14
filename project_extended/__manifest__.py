# -*- coding: utf-8 -*-
{
    'name': "Personalizacion de Proyectos",

    'summary': """
        Personalización de Proyectos""",

    'description': """
        Se agrega / modifica lo siguiente en proyectos:\n
        - Campo Fecha Inicio / Fecha Fin: lo cual será registrado por el usuario.\n
        - Campo Inicio Real / Fin Real: lo cual será auto-calculado mediante los registros de Parte de Horas.\n
        - Campo Prioridad: En Tarea se agrega la prioridad Alta / Media / Baja.\n
        - Campo Tipo de Tarea: En Tarea se agrega el Tipo de Tarea.
        """,

    'author': "TH",
    'website': "http://www.cabalcon.com",

    'category': 'Services/Project',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
    	#'security/ir.model.access.csv',
    	'views/project_task_view.xml',
    ],
}
