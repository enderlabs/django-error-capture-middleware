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
Error caprture middleware and default application.
"""

import platform
import sys

from django.conf import settings
from django import http

# Imports based on version
if platform.python_version() >= '2.6.0':
    threading = __import__('multiprocessing')
    thread_cls = threading.Process
    queue_mod = __import__('multiprocessing.queues', fromlist=[True])
else:
    threading = __import__('threading')
    thread_cls = threading.Thread
    queue_mod = __import__('queue')


class ErrorCaptureMiddleware(object):
    """
    Middleware to capture exceptins and create a ticket/bug for it.
    """

    def process_exception(self, request, exception):
        """
        Process the exception.

        :Parameters:
           - `request`: request that caused the exception
           - `exception`: actual exception being raised
        """
        if isinstance(exception, http.Http404):
            raise exception
        handler_count = len(settings.ERROR_CAPTURE_HANDLERS)
        count = 0
        for handler in settings.ERROR_CAPTURE_HANDLERS:
            module = '.'.join(handler.split('.')[:-1])
            cls = handler.split('.')[-1]
            handler_obj = getattr(__import__(module, fromlist=[True]), cls)
            count += 1
            func = handler_obj()
            if (settings.ERROR_CAPTURE_ENABLE_MULTPROCESS
                and count < handler_count):
                a_process = thread_cls(
                    target=func, args=(request, exception, sys.exc_info()))
                #a_process.daemon = True
                a_process.start()
            else:
                result = func(request, exception, sys.exc_info())
            # If it is the last item, then it will be what we return.
            if count >= handler_count:
                return result


class ErrorCaptureHandler(object):
    """
    Parent class for creating a handler.
    """

    traceback = __import__('traceback')

    def handle(self, request, exception, tb):
        """
        Must be defined in a subclass. Takes care of processing the
        exception.

        :Parameters:
           - `request`: request causing the exception
           - `exception`: actual exception raised
           - `tb`: traceback string
        """
        raise NotImplementedError('You must define handle')

    def background_call(self, callback, args=(), kwargs={}):
        """
        Provides a simple interface for doing background processing.
        An object providing a get method is returned along with the
        process or thread object.

        :Parameters:
           - `callback`: callable to execute
           - `args`: non-keyword arguments to pass to callback
           - `kwargs`: keyword arguments to pass to callback
        """
        a_queue = queue_mod.Queue()
        kwargs.update({'queue': a_queue})
        if settings.ERROR_CAPTURE_ENABLE_MULTPROCESS:
            a_process = thread_cls(target=callback, args=args, kwargs=kwargs)
            a_process.daemon = True
            a_process.start()
        else:
            a_process = callback(*args, **kwargs)
        return a_queue, a_process

    def __call__(self, request, exception, exc_info):
        """
        Actually gets called from the middleware and takes care of 
        adding in the traceback information.

        :Parameters:
           - `request`: request causing the exception
           - `exception`: actual exception raised
           - `exc_info`: info from sys.exc_info
        """
        return self.handle(
            request, exception, self.traceback.format_exception(*exc_info))
