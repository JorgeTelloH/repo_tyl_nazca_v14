{
    'name': 'Tipo de Elemento de Cuenta',
    'version': '1.1.0',
    'category': 'Accounting',
    'license': 'AGPL-3',
    'summary': "Modulo que permite determinar un Tipo de Elemento de Cuenta",
    'author': "Franco Najarro (Cabalcon)",
    'website': 'www.cabalcon.com.pe',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/data_element_config_view.xml',
        'views/element_config_view.xml',
        'views/account_view.xml',
        ],
    'installable': True,
}
