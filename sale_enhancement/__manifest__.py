{
    'name': 'Sale Enhancement',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Extends Sales module with deadline and priority features in odoo18',
    'description': """
        This module enhances the Sales module with:
        - Delivery deadline tracking
        - Priority levels
        - Deadline overdue calculations
        - Automated cron jobs
        - Enhanced security rules
    """,
    'author': 'Nihala CP',
    'website': 'https://www.yourwebsite.com',
    'depends': ['sale', 'base'],
    'data': [
        'data/cron_data.xml',
        'security/groups.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}