{
    'name': 'Product Multiple Images Upload',
    'author': 'Opsway',
    'version': '16.0.1.0',
    'website': 'https://www.opsway.com',
    'category': 'Sales',
    'description': 'Module to upload multiple images for a product',
    'summary': """
        Module to upload multiple images for a product
    """,
    'depends': ['corsiva_lazada'],
    'data': [
        # 'views/view.xml',
        'views/lazada_product_views.xml',
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'corsiva_upload_multi_image/static/src/*.js',
            'corsiva_upload_multi_image/static/src/*.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
