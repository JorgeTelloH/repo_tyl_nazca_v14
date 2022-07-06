{
	'name': 'SUNAT PLE - Libros Base',
	'version': "1.1.0",
	'author': 'Franco Najarro (Cabalcon)',
	'website':'www.cabalcon.com.pe',
	'category':'Accounting',
	'depends':['base', 'account','report_formats'],
	'description':'''
		Modulo de reportes.
			> Base
		''',
	'data':[
		'security/group_users.xml',
		'security/ir.model.access.csv',
		'views/ple_base_view.xml',
		'views/res_country_view.xml',
	],
	'installable': True,
    'auto_install': False,
}