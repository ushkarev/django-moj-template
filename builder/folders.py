import os
import re


class FolderStructure:
    name = ''

    def __init__(self, path):
        self.path = path

    def _get_full_path(self, *paths):
        return os.path.join(self.path, *paths)


class Repository(FolderStructure):
    git_url = ''
    version = None

    def __init__(self, path):
        super().__init__(path)
        self.path = self._get_full_path(self.name)


class DjangoAppPackage(FolderStructure):
    name = 'django_moj_template'

    def __init__(self, path):
        super().__init__(path)
        self.build_flag_path = self._get_full_path('.build-date')
        self.app_path = self._get_full_path(self.name)
        self.static_path = self._get_full_path(self.name, 'static')
        self.images_path = self._get_full_path(self.name, 'static', 'images')
        self.javascripts_path = self._get_full_path(self.name, 'static', 'javascripts')
        self.stylesheets_path = self._get_full_path(self.name, 'static', 'stylesheets')
        self.templates_path = self._get_full_path(self.name, 'templates')
        self.assets_src_path = self._get_full_path(self.name, 'assets-src')


class GOVUKTemplate(Repository):
    name = 'govuk_template'
    git_url = 'https://github.com/alphagov/govuk_template.git'

    def __init__(self, path):
        super().__init__(path)
        self.pkg_root_path = self._get_full_path('pkg')
        self.pkg_path = None
        self.app_path = None

    def find_pkg_path(self):
        """
        Finds the built python package folder
        e.g. django_govuk_template-0.17.0
        """
        if not self.pkg_path:
            def matcher(path):
                if not os.path.isdir(os.path.join(self.pkg_root_path, path)):
                    return False
                matches = re.match(r'^django_govuk_template-(?P<version>.*)$', path)
                if not matches:
                    return False
                self.version = matches.group('version')
                return True

            pkg_path = list(filter(matcher, os.listdir(self.pkg_root_path)))
            if len(pkg_path) != 1:
                return None
            self.pkg_path = os.path.join(self.pkg_root_path, pkg_path[0])

        return self.pkg_path

    def find_app_path(self):
        """
        Finds the path to the Django app inside the package
        """
        if not self.app_path:
            if not self.pkg_path:
                return None
            app_path = os.path.join(self.pkg_path, 'govuk_template')
            if not os.path.isdir(app_path):
                return None
            self.app_path = app_path

        return self.app_path


class GOVUKElements(Repository):
    name = 'govuk_elements'
    git_url = 'https://github.com/alphagov/govuk_elements.git'

    def __init__(self, path):
        super().__init__(path)
        # these do not exist until gulp tasks run:
        self.content_path = self._get_full_path('govuk_modules', 'public')
        self.elements_sass_path = self._get_full_path('public', 'sass')
