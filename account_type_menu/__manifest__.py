# -*- coding: utf-8 -*-
{
    'name': 'Tipo de Cuenta Contable',
    'summary': 'Mostrar el Tipo de cuenta usado en el plan de contable',
    'description': """Ver el Tipo de cuenta usado en el plan de contable.\n
		Configuración:\n
		Ir al módulo de Contabilidad / Configuración ==> Tipos de Cuenta Contable\n
		En esta se podrá agregar, reemplazar o actualizar el tipo de cuenta.""",
	'author': 'TH',
	'website': 'http://www.cabalcon.com',

	'category': 'Accounting',
	'version': '1.1',

	# any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/account_type_menu.xml'
    ],
}