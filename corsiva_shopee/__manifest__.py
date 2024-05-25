{
    'name': "Shopee Connector",
    'summary': """ Corsiva's ERP system integrates with shopee """,
    'description': """ Synchronize orders and products between odoo and shopee """,
    'author': "gosu28",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '16.0.0.0',
    'depends': [
        'base',
        'corsiva_connector',
        'sale_management',
        'sale_stock',
        'contacts'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/shopee_config_settings_views.xml',
        'views/shopee_product_category_views.xml',
        # 'views/shopee_partner_views.xml',
        'views/shopee_product_views.xml',
        'views/product_logistic.xml',
    ],
    'demo': [],
    'application': True
}
