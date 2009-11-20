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

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import mail_admins
from django.shortcuts import render_to_response
from django.template import Context, loader

from error_capture_middleware import ErrorCaptureHandler
from error_capture_middleware.models import Error


class EmailHandler(ErrorCaptureHandler):
    """
    Replacement email handler.
    """

    def handle(self, request, exception, tb):
        """
        Turns the resulting traceback into something emailed back to admins.

        :Parameters:
           - `request`: request causing the exception
           - `exception`: actual exception raised
           - `tb`: traceback string
        """
        try:
            admins = settings.ADMINS
            fail_silently = settings.ERROR_CAPTURE_EMAIL_FAIL_SILENTLY
            server_email = settings.SERVER_EMAIL
        except:
            raise ImproperlyConfigured(
                'You must define SERVER_EMAIL, ADMINS and '
                'ERROR_CAPTURE_EMAIL_FAIL_SILENTLY in your settings.')
        data = {'traceback': tb}
        data.update(request.META)
        context = Context(data)
        # Worker function
        def get_data(queue):
            subject_tpl = loader.get_template(
                'error_capture_middleware/email/subject.txt')
            body_tpl = loader.get_template(
                'error_capture_middleware/email/body.txt')
            # The render function appends a \n character at the end. Subjects
            # can't have newlines.
            subject = subject_tpl.render(context).replace('\n','')
            body = body_tpl.render(context)

            mail_admins(subject, body, fail_silently=fail_silently)
        queue, process = self.background_call(get_data)
        return render_to_response('error_capture_middleware/error.html', {})
