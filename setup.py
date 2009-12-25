#!/usr/bin/env python
#
# This file is part of pipestat.
#
# pipestat is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pipestat is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pipestat.  If not, see <http://www.gnu.org/licenses/>.
"""
Standard build script.
"""

__docformat__ = 'restructuredtext'

import os
import sys

from setuptools import setup, find_packages, Command

sys.path.insert(0, 'src')

from example_project.manage import execute_manager, settings


class TestCommand(Command):
    """
    Execute Django unittests.
    """

    description = __doc__[1:-1]

    # Required but unused items.
    user_options = []
    initialize_options = finalize_options = lambda s: None

    run = lambda s: execute_manager(settings)
    run.__doc__ = "Execute the unittests."


setup(
    name="error_capture_middleware",
    version='0.0.1',
    description="sends tracebacks in Django to bugtrackers or services",
    long_description=("Middleware for the Django framework that allows you "
        "to send tracebacks to bugtrackers or other services through the use "
        "of handlers. Helpful for keeping track of issues and avoiding the "
        "flood of error emails that most frameworks default with."),
    author="Steve 'Ashcrow' Milner",
    author_email='stevem@gnulinux.net',
    url="http://bitbucket.org/ashcrow/django-error-capture-middleware/",
    download_url=("http://bitbucket.org/ashcrow/"
        "django-error-capture-middleware/downloads/"),

    license="New BSD",

    packages=find_packages('src'),

    package_dir={'': 'src'},

    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python',
    ],
    cmdclass={
        'test': TestCommand,
    },
)
