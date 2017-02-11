# Copyright 2017, Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# (c) 2017, Kevin Carter <kevin.carter@rackspace.com>

import traceback

from oslo_log import log as logging


LOG = logging.getLogger(__name__)


class _BaseException(Exception):
    def __init__(self, *args):
        if len(args) > 1:
            format_message = args[0]
            try:
                message = format_message % tuple(args[1:])
            except TypeError as exp:
                message = (
                    'The exception message was not formatting correctly.'
                    ' Error: [ %s ]. This was the data passed: "%s"'
                    % (exp, args)
                )
        else:
            message = args[0]

        super(_BaseException, self).__init__(message)
        LOG.error(message)


class InvalidRequest(_BaseException):
    """Request was Invalid."""
    pass


def log_exception(exp):
    """Return log entries.

    :param exp: Exception object
    :type exp: string || object
    :return: string
    """
    _trace = [i.strip() for i in str(traceback.format_exc()).splitlines()]
    trace = ' -> '.join(_trace)
    _exception = [i.strip() for i in str(exp).splitlines()]
    exception = ' -> '.join(_exception)
    return 'Exception [ %s ]: %s' % (exception, trace)
