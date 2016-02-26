import argparse
from collections import OrderedDict
import datetime
import filecmp
import os
import re
import subprocess
import sys
import textwrap

from builder.folders import DjangoAppPackage, GOVUKTemplate, GOVUKElements
from builder.utils import announce_calls, one_line_doc, requisites, term_bold

commands = OrderedDict()


def command(func):
    """
    Decorator to make a method available as a command
    :param func: the callable to decorate
    """
    name = func.__name__
    commands[name] = {
        'command': func,
        'name': name,
    }
    return func


class Builder:
    """
    Builds a python package containing a Django app with
    the latest gov.uk template and elements
    """

    def __init__(self, root_path):
        self.root_path = root_path
        self.template_path = os.path.join(root_path, 'builder', 'template')
        self.src_path = os.path.join(root_path, 'src')

        self.source_repositories = [
            GOVUKTemplate(self.src_path),
            GOVUKElements(self.src_path),
        ]
        self.package = DjangoAppPackage(os.path.join(root_path, 'build'))

        self.parser = argparse.ArgumentParser(description=textwrap.dedent(self.__doc__).strip())
        self.parser.add_argument('command', choices=[option['name'] for option in commands.values()])
        self.parser.add_argument('--optimise-images', dest='should_optimise_images', action='store_true')
        self.parser.add_argument('-v', '--verbose', action='store_true')
        args = self.parser.parse_args()
        self.command = args.command
        self.verbose = args.verbose
        self.should_optimise_images = args.should_optimise_images

    def main(self):
        commands[self.command]['command'](self)

    @command
    def help(self):
        """
        Prints this help message
        """
        print(self.parser.description)
        print('Commands:')
        max_comand_length = max(len(option['name']) for option in commands.values()) + 2
        for option in commands.values():
            name = option['name']
            print('  %s' % name + ' ' * (max_comand_length - len(name)) + one_line_doc(option['command']))

    # BUILDING

    @announce_calls('Checking build tools are available')
    def check_build_tools(self):
        def check(name, version, cmd, version_re):
            version_tuple = tuple(version.split('.'))
            try:
                output = subprocess.check_output(cmd).decode('utf-8')
                output = re.match(version_re, output, re.I)
                if not output or output.groups([1, len(version_tuple)]) < version_tuple:
                    sys.exit('%s on the path must be at least version %s' % (name, output))
            except subprocess.CalledProcessError:
                sys.exit('%s is not on the path' % name)

        # check('Ruby', '2.2', ['ruby', '--version'], r'ruby (\d+)\.(\d+)\.')
        # check('Python', '3.4', ['python', '--version'], r'Python (\d+)\.(\d+)\.')
        check('bundler', '1.10', ['bundler', '--version'], r'Bundler version (\d+)\.(\d+)\.')
        check('npm', '3.7', ['npm', '--version'], r'(\d+)\.(\d+)\.')
        check('sass', '3.4', ['sass', '--version'], r'Sass (\d+)\.(\d+)\.')

    def make_paths(self):
        self.make_paths(self.src_path, self.package.static_path, self.package.templates_path)

    @announce_calls('Updating source repositories')
    def update_source_repositories(self):
        for repo in self.source_repositories:
            if os.path.isdir(repo.path):
                subprocess.check_call(['git', 'pull'], cwd=repo.path)
            else:
                subprocess.check_call(['git', 'clone', '--recursive',
                                      repo.git_url, repo.name], cwd=self.src_path)

    @classmethod
    def fix_ruby_version(cls, path):
        path = os.path.join(path, '.ruby-version')
        if not os.path.exists(path):
            sys.exit('No ruby version specified')
        with open(path) as f:
            ruby_version = f.read().strip()
        try:
            ruby_version_tuple = tuple(map(int, ruby_version.split('.')))
            if len(ruby_version_tuple) < 3 or ruby_version_tuple < (2, 2, 0):
                raise ValueError
        except ValueError:
            print(term_bold('Fixing ruby version to 2.2.3 (was %s)') % (ruby_version or '?'))
            with open(path, 'w') as f:
                f.write('2.2.3')

    @command
    @requisites(check_build_tools, make_paths, update_source_repositories)
    @announce_calls('Done', after_call=True)
    def build(self):
        """
        Builds the complete python package
        """
        for repo in self.source_repositories:
            getattr(self, 'build__%s' % repo.name)(repo)

        if self.should_optimise_images:
            self.optimise_images()
        self.create_django_app()

    @announce_calls('Building gov.uk template')
    def build__govuk_template(self, repo):
        self.fix_ruby_version(repo.path)
        subprocess.check_call(['bundle', 'install'], cwd=repo.path)
        subprocess.check_call(['bundle', 'exec', 'rake', 'build:django'], cwd=repo.path)

        if not repo.find_pkg_path():
            sys.exit('Could not find built package')
        if not repo.find_app_path():
            sys.exit('Cannot find built package app content')

        # copy built content
        self.rsync_folders(repo.app_path, self.package.app_path)

    @announce_calls('Building gov.uk elements')
    def build__govuk_elements(self, repo):
        subprocess.check_call(['npm', 'install'], cwd=repo.path)

        # build assets
        grunt_tasks = ['grunt']
        grunt_tasks.extend([
            # grunt tasks are a limited set taken from "default" task
            'copy:govuk_template',
            'copy:govuk_assets',
            'copy:govuk_frontend_toolkit_scss',
            'copy:govuk_frontend_toolkit_js',
            'copy:govuk_frontend_toolkit_img',
            'replace',
            'sass',
        ])
        subprocess.check_call(grunt_tasks, cwd=repo.path)

        # copy built content
        self.rsync_folders_and_warn(repo.content_path, self.package.static_path,
                                    'GOV.UK Elements overwrites %(count)d asset(s) from GOV.UK Template')

        # move sass files to assets folder (originating from govuk_frontend_toolkit?)
        self.rm_paths(self.package.assets_src_path)
        subprocess.check_call([
            'mv', os.path.join(self.package.static_path, 'sass'), self.package.assets_src_path
        ])

        # copy additional elements sass to assets folder
        self.rsync_folders_and_warn(repo.elements_sass_path, self.package.assets_src_path,
                                    'GOV.UK Elements build overwrites %(count)d asset(s)')

        # build sass files to static folder (originating from govuk_elements?)
        self.fix_sass_images_path(self.package.assets_src_path)
        sass_paths = '.:%s' % self.package.stylesheets_path
        subprocess.check_call(['sass', '--no-cache', '--sourcemap=none', '--update', sass_paths],
                              cwd=self.package.assets_src_path)

    @classmethod
    def fix_sass_images_path(cls, path):
        path = os.path.join(path, 'elements', '_helpers.scss')
        with open(path) as f:
            helper_sass = f.read()
        helper_sass = re.sub(r'/public/', '../', helper_sass)
        with open(path, 'w') as f:
            f.write(helper_sass)

    def optimise_images(self):
        """
        Use ImageOptim to optimise images on OS X only
        https://imageoptim.com/
        """
        if sys.platform != 'darwin':
            return
        try:
            app_path = subprocess.check_output(['mdfind', 'kMDItemCFBundleIdentifier == "net.pornel.ImageOptim"'])
        except subprocess.CalledProcessError:
            return
        app_path = app_path.strip().decode('utf-8').splitlines()
        if not app_path:
            return
        app_path = app_path[0]
        bin_path = '%s/Contents/MacOS/ImageOptim' % app_path
        if not os.path.exists(bin_path):
            return

        print(term_bold('Optimising images… this may take a while!'))
        subprocess.check_call([bin_path, self.package.images_path, self.package.stylesheets_path])

    @announce_calls('Creating Django app')
    def create_django_app(self):
        # add templated files
        self.rsync_folders(self.template_path, self.package.path)

        # tidy up
        subprocess.check_call(['find', '.',
                               '-name', '.DS_Store', '-or',
                               '-name', '*.mo', '-or',
                               '-name', '*.py?', '-or',
                               '-path', '"*/.sass-cache*"',
                               '-delete'],
                              cwd=self.package.path)

        # mark build as complete
        with open(self.package.build_flag_path, 'w') as f:
            f.write(str(datetime.datetime.now()))

    # PUBLISHING

    @command
    @announce_calls('Done', after_call=True)
    def publish(self):
        """
        Publishes the python package to PyPi
        """
        if not os.path.exists(self.package.build_flag_path):
            sys.exit('Run the build command first before trying to publish')
        subprocess.check_call(['python', 'setup.py', 'sdist', 'upload'],
                              cwd=self.package.path)

    # CLEANING

    @command
    def clean(self):
        """
        Clean up sources and builds
        """
        self.rm_paths(self.src_path, self.package.path)

    # UTILS

    @classmethod
    def make_paths(cls, *paths):
        for path in paths:
            if os.path.isdir(path):
                continue
            os.makedirs(path, 0o755)

    @classmethod
    def rm_paths(cls, *paths):
        for path in paths:
            if not os.path.exists(path):
                continue
            subprocess.check_call(['rm', '-rf', path])

    @classmethod
    def rsync_folders(cls, src_path, target_path):
        subprocess.check_call(['rsync', '-r', src_path.rstrip('/') + '/', target_path.rstrip('/')])

    @classmethod
    def diff_folders(cls, src_root_path, target_root_path, track_new=True):
        differences = []
        for dir_path, dir_names, file_names in os.walk(src_root_path):
            relative_dir_path = os.path.relpath(dir_path, src_root_path)
            target_dir_path = os.path.abspath(os.path.join(target_root_path, relative_dir_path))
            for file_name in file_names:
                relative_file_path = os.path.join(relative_dir_path, file_name)
                src_file_path = os.path.join(dir_path, file_name)
                target_file_path = os.path.join(target_dir_path, file_name)
                if not os.path.exists(target_file_path):
                    if track_new:
                        differences.append((relative_file_path, 'new'))
                elif not filecmp.cmp(src_file_path, target_file_path):
                    differences.append((relative_file_path, 'modified'))
        return differences

    @classmethod
    def rsync_folders_and_warn(cls, src_path, target_path, message):
        differences = cls.diff_folders(src_path, target_path, track_new=False)
        if differences:
            print(term_bold(message % {
                'count': len(differences)
            }))
            for difference in differences:
                print('  %s' % difference[0])
        cls.rsync_folders(src_path, target_path)
