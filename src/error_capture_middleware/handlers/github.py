# Copyright (c) 2009, Steve 'Ashcrow' Milner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#    * Neither the name of the project nor the names of its
#      contributors may be used to endorse or promote products
#      derived from this software without specific prior written
#      permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Super simple ticket handler that uses the admin interface.
"""

import yaml
import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render_to_response
from django.template import Context, loader

from error_capture_middleware import ErrorCaptureHandler
from error_capture_middleware.models import Error


# TODO maybe we can add some nice methods to help take care of some what
# will be used in other backends ... need to find out what they will be

class GitHubHandler(ErrorCaptureHandler):
    """
    Default handler of errors.
    """

    def handle(self, request, exception, tb):
        """
        Must be defined in a subclass. Takes care of processing the
        exception.

        :Parameters:
           - `request`: request causing the exception
           - `exception`: actual exception raised
           - `tb`: traceback string
        """
        try:
            repo = settings.ERROR_CAPTURE_GITHUB_REPO
            token = settings.ERROR_CAPTURE_GITHUB_TOKEN
            login = settings.ERROR_CAPTURE_GITHUB_LOGIN
        except:
            raise ImproperlyConfigured(
                'You must define ERROR_CAPTURE_GITHUB_LOGIN, '
                'ERROR_CAPTURE_GITHUB_TOKEN, ERROR_CAPTURE_GITHUB_REPO '
                'in your settings.')
        url = "http://github.com/api/v2/yaml/issues/open/" + repo
        issue_url =' http://github.com/'+repo+'/issues#issue/'
        # Make the data nice for github
        data = {'traceback': tb}
        data.update(request.META)
        context = Context(data)
        title_tpl = loader.get_template(
            'error_capture_middleware/github/title.txt')
        body_tpl = loader.get_template(
            'error_capture_middleware/github/body.txt')
        params = {
            'login': login,
            'token': token,
            'title': title_tpl.render(context),
            'body': body_tpl.render(context),
        }
        result = urllib.urlopen(url, urllib.urlencode(params)).read()
        # Remove !timestamp, it isn't valid
        id = yaml.load(result.replace('!timestamp', ''))['issue']['number']
        return render_to_response('error_capture_middleware/error.html',
            {'bug_url': issue_url + str(id), 'id': id})
