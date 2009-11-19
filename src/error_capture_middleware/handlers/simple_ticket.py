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

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render_to_response

from error_capture_middleware import ErrorCaptureHandler
from error_capture_middleware.models import Error


class SimpleTicketHandler(ErrorCaptureHandler):
    """
    Default handler of errors.
    """

    def handle(self, request, exception, tb):
        """
        Pushes the traceback into a simple ticket system.

        :Parameters:
           - `request`: request causing the exception
           - `exception`: actual exception raised
           - `tb`: traceback string
        """
        user = None
        if isinstance(request.user, User):
            user = request.user
        error = Error(user=user, traceback="\n".join(tb))
        error.save()
        return render_to_response('error_capture_middleware/error.html',
            {'id': error.id})
