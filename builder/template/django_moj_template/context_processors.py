from django.utils.translation import get_language, ugettext as _


def moj_context(request):
    return {
        'html_lang': get_language(),
        'homepage_url': 'https://www.gov.uk/',
        'logo_link_title': _('Go to the GOV.UK homepage'),
        'global_header_text': _('GOV.UK'),
        'skip_link_message': _('Skip to main content'),
        'crown_copyright_message': _('© Crown copyright')
    }
