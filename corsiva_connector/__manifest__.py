{
    'name': "Connector Base",
    'summary': """ Original connection module """,
    'description': """ Build the original connection module by calling the api """,
    'author': "gosu28",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '16.0.0.0',
    'depends': [
            'base',
            'sale_stock',
            'contacts',
            'sale_management',
                ],
    'data': [
        # 'security/ir.model.access.csv'
        'views/corsiva_product_view.xml',
        'views/corsiva_partner_view.xml',
        'views/corsiva_order_view.xml',
        'views/configuration.xml',
    ],
    'demo': []
}
