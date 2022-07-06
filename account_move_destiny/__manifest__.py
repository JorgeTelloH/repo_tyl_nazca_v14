# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009-TODAY Odoo Peru(<http://www.odooperu.pe>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name' : 'Asiento Destino',
    'version' : '1.0',
    'author' : 'Oswaldo Lopez Cabalcon',
    'category' : 'Accounting & Finance',
    'summary': 'Asiento destino automaticos al publicar un asiento.',
    'license': 'AGPL-3',
    'description' : """
Cuentas destino automaticos al publicar un asiento.

    """,
    'website': "http://www.cabalcon.com",
    'depends' : ['account','account_pe','account_cost_center'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/analytic_account_view.xml',
        'views/account_move_destiny_view.xml',
        'views/res_config_settings.xml',
        'views/account_cost_center.xml',
    ],
    'qweb' : [

    ],
    'images': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "sequence": 1,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
