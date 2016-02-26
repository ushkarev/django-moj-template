def sample_context(request):
    return {
        'phase': 'beta',
        'proposition': {
            'name': 'Proposition title',
            'links': [
                {
                    'name': 'Link #1',
                    'url': '#',
                },
                {
                    'name': 'Link #2, active',
                    'url': '#',
                    'active': True,
                },
                {
                    'name': 'Link #3',
                    'url': '#',
                },
            ]
        },
        'footer_support_links': [
            {
                'name': 'Privacy Policy',
                'url': '#',
            },
            {
                'name': 'Cookies',
                'url': '#',
            },
        ],
    }
