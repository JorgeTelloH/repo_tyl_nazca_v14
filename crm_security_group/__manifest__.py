# -*- coding: utf-8 -*-
{
    "name": "CRM Only Security Groups",
    "summary": "Add new group in Sales to show only CRM",
    "version": "14.0.1.0.1",
    "category": "Customer Relationship Management",
    "website": "https://github.com/OCA/crm",
    "author": "Tecnativa, Odoo Community Association (OCA), TH",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["crm", "sale_crm"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/menu_items.xml",
    ],
}
