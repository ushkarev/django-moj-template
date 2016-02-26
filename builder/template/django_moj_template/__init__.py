default_app_config = 'django_moj_template.app.AppConfig'


def get_assets_src_path():
    """
    Returns the path to the assets folder where sass files are stored
    """
    from os import path

    return path.abspath(path.join(path.dirname(path.join(__file__)), 'assets-src'))
