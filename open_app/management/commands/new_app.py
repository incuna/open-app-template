import errno
from optparse import make_option
import os
import re
import shutil

from django.core.management import BaseCommand, CommandError
from django.core.management.commands.makemessages import handle_extensions
from django.core.management.templates import TemplateCommand
from django.template import Template, Context
from django.utils._os import rmtree_errorhandler

import open_app


class Command(TemplateCommand):
    args = '[target directory] [optional python name]'
    option_list = BaseCommand.option_list + (
        make_option('--template', action='store',
                    dest='template',
                    help='The path to load the template from.'),
        make_option('--extension', '-e', dest='extensions',
                    action='append', default=['py', 'rst', 'md'],
                    help='The file extension(s) to render (default: "py,rst,md"). '
                         'Separate multiple extensions with commas, or use '
                         '-e multiple times.'),
        make_option('--name', '-n', dest='files',
                    action='append', default=['Makefile', 'LICENSE'],
                    help='The file name(s) to render. Needed for files without extensions. '
                         'Default is Makefile, LICENSE. '
                         'Separate multiple extensions with commas, or use '
                         '-n multiple times.')
        )

    def handle(self, target=None, import_name=None, *args, **options):
        if target is None:
            raise CommandError("you must provide a target")
        self.app_or_project = app_or_project = 'project'
        self.paths_to_remove = []
        self.verbosity = int(options.get('verbosity'))
        options['import_name'] = import_name

        if not options['template']:
            options['template'] = os.path.join(os.path.dirname(open_app.__file__), 'app_name')

        # if some directory is given, make sure it's nicely expanded
        if target is None:
            top_dir = os.path.join(os.getcwd(), name)
            try:
                os.makedirs(top_dir)
            except OSError as e:
                if e.errno == errno.EEXIST:
                    message = "'%s' already exists" % top_dir
                else:
                    message = e
                raise CommandError(message)
        else:
            top_dir = os.path.abspath(os.path.expanduser(target))
            if not os.path.exists(top_dir):
                raise CommandError("Destination directory '%s' does not "
                                   "exist, please create it first." % top_dir)

        options['app_name'] = name = os.path.basename(top_dir)

        # generate the import name if it's not provided
        if import_name is None:
            import_name = name.replace('-', '_')

        # If it's not a valid directory name.
        if not re.search(r'^[_a-zA-Z]\w*$', import_name):
            # Provide a smart error message, depending on the error.
            if not re.search(r'^[_a-zA-Z]', import_name):
                message = ('make sure the name begins '
                           'with a letter or underscore')
            else:
                message = 'use only numbers, letters and underscores'
            raise CommandError("%r is not a valid python name. Please %s." %
                               (import_name, message))

        extensions = tuple(
            handle_extensions(options.get('extensions'), ignored=()))
        extra_files = []
        for file in options.get('files'):
            extra_files.extend(map(lambda x: x.strip(), file.split(',')))
        if self.verbosity >= 2:
            self.stdout.write("Rendering %s template files with "
                              "extensions: %s\n" %
                              (app_or_project, ', '.join(extensions)))
            self.stdout.write("Rendering %s template files with "
                              "filenames: %s\n" %
                              (app_or_project, ', '.join(extra_files)))

        base_name = '%s_name' % app_or_project
        base_subdir = '%s_template' % app_or_project
        base_directory = '%s_directory' % app_or_project

        context = Context(dict(options, **{
            base_name: name,
            base_directory: top_dir,
        }), autoescape=False)

        # Setup a stub settings environment for template rendering
        from django.conf import settings
        if not settings.configured:
            settings.configure()

        template_dir = self.handle_template(options.get('template'),
                                            base_subdir)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = os.path.join(top_dir, relative_dir)
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if dirname.startswith('.'):
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(top_dir, relative_dir,
                                     filename.replace(base_name, name))
                if os.path.exists(new_path):
                    raise CommandError("%s already exists, overlaying a "
                                       "project or app into an existing "
                                       "directory won't replace conflicting "
                                       "files" % new_path)

                # Only render the Python files, as we don't want to
                # accidentally render Django templates files
                with open(old_path, 'r') as template_file:
                    content = template_file.read()
                if filename.endswith(extensions) or filename in extra_files:
                    template = Template(content)
                    content = template.render(context)
                with open(new_path, 'w') as new_file:
                    new_file.write(content)

                if self.verbosity >= 2:
                    self.stdout.write("Creating %s\n" % new_path)
                try:
                    shutil.copymode(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path, self.style.NOTICE)

        inner_module_dir = os.path.join(top_dir, 'import_name')
        if os.path.exists(inner_module_dir):
            shutil.move(inner_module_dir, os.path.join(top_dir, import_name))

        if self.paths_to_remove:
            if self.verbosity >= 2:
                self.stdout.write("Cleaning up temporary files.\n")
            for path_to_remove in self.paths_to_remove:
                if os.path.isfile(path_to_remove):
                    os.remove(path_to_remove)
                else:
                    shutil.rmtree(path_to_remove,
                                  onerror=rmtree_errorhandler)
