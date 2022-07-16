# -*- encoding: utf-8 -*-

{
    'name': 'Tipo de Cambio Especial/Fecha Emisión',
    'summary': """
    	Tipo de Cambio Especial
    """,
    'version': '14.0',
    'category': 'Accounting',
    'description': """
       El usuario puede usar el Tipo de Cambio Especial para modificar este dato en:\n
       - Comprobantes de Cliente\n
       - Comprobantes de Proveedor
    """,
    'author': 'Franco Najarro / TH (Cabalcon)',
    'website': 'www.cabalcon.com',
    'depends': ['sale', 'account', 'odoope_currency'],
    'data': [
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/account_payment_register_view.xml'
    ],
}
