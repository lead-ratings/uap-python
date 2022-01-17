#!/usr/bin/env python
import os
from distutils import log
from distutils.core import Command
from distutils.command.build import build as _build
from setuptools import setup
from setuptools.command.develop import develop as _develop
from setuptools.command.sdist import sdist as _sdist
from setuptools.command.install import install as _install


def check_output(*args, **kwargs):
    from subprocess import Popen
    proc = Popen(*args, **kwargs)
    output, _ = proc.communicate()
    rv = proc.poll()
    assert rv == 0, output


class build_regexes(Command):
    description = 'build supporting regular expressions from uap-core'
    user_options = [
        ('work-path=', 'w',
         "The working directory for source files. Defaults to ."),
        ('build-lib=', 'b',
         "directory for script runtime modules"),
        ('inplace', 'i',
         "ignore build-lib and put compiled javascript files into the source " +
         "directory alongside your pure Python modules"),
        ('force', 'f',
         "Force rebuilding of static content. Defaults to rebuilding on version "
         "change detection."),
    ]
    boolean_options = ['force']

    def initialize_options(self):
        self.build_lib = None
        self.force = None
        self.work_path = None
        self.inplace = None

    def finalize_options(self):
        install = self.distribution.get_command_obj('install')
        sdist = self.distribution.get_command_obj('sdist')
        build_ext = self.distribution.get_command_obj('build_ext')

        if self.inplace is None:
            self.inplace = (build_ext.inplace or install.finalized
                            or sdist.finalized) and 1 or 0

        if self.inplace:
            self.build_lib = '.'
        else:
            self.set_undefined_options('build',
                                       ('build_lib', 'build_lib'))
        if self.work_path is None:
            self.work_path = os.path.realpath(os.path.join(os.path.dirname(__file__)))

    def run(self):
        work_path = self.work_path
        if not os.path.exists(os.path.join(work_path, '.git')):
            return

        log.info('initializing git submodules')
        check_output(['git', 'submodule', 'init'], cwd=work_path)
        check_output(['git', 'submodule', 'update'], cwd=work_path)

        self.update_manifest()

        log.info('all done')

    def update_manifest(self):
        sdist = self.distribution.get_command_obj('sdist')
        if not sdist.finalized:
            return

        sdist.filelist.files.append('old_ua_parser/_regexes.py')


class develop(_develop):
    def run(self):
        self.run_command('build_regexes')
        _develop.run(self)


class install(_install):
    def run(self):
        self.run_command('build_regexes')
        _install.run(self)


class build(_build):
    def run(self):
        self.run_command('build_regexes')
        _build.run(self)


class sdist(_sdist):
    sub_commands = _sdist.sub_commands + [('build_regexes', None)]


cmdclass = {
    'sdist': sdist,
    'develop': develop,
    'build': build,
    'install': install,
    'build_regexes': build_regexes,
}


setup(
    name='old-ua-parser',
    version='0.7.1',
    description="Python port of Browserscope's user agent parser",
    author='PBS',
    author_email='no-reply@pbs.org',
    packages=['old_ua_parser'],
    package_dir={'': '.'},
    license='LICENSE.txt',
    zip_safe=False,
    url='https://github.com/ua-parser/uap-python',
    include_package_data=True,
    setup_requires=['pyyaml'],
    install_requires=[],
    cmdclass=cmdclass,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
