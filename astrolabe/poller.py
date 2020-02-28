# Copyright 2020-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for polling a set of entities."""

import logging
from time import sleep

from astrolabe.exceptions import PollingTimeoutError
from astrolabe.utils import Timer


LOGGER = logging.getLogger(__name__)


class PollerBase:
    """Base class for implementing a poller."""
    def __init__(self, *, frequency, timeout):
        self.interval = 1.0 / frequency
        self.timeout = timeout

    @staticmethod
    def _check_ready(obj, attribute, args, kwargs):
        """Abstract method that defines the readiness check used during
        polling."""
        raise NotImplementedError

    def poll(self, objects, *, attribute, args, kwargs):
        """Wait for a member of `objects` to become ready. Once a member
        is ready, return it to the caller. The values of `attribute`,
        `args` and `kwargs` depends on the readiness check employed by the
        implementation."""
        timer = Timer()
        timer.start()
        while timer.elapsed < self.timeout:
            logmsg = "Polling {} [elapsed: {:.2f} seconds]"
            LOGGER.debug(logmsg.format(objects, timer.elapsed))
            for obj in objects:
                return_value = self._check_ready(obj, attribute, args, kwargs)
                if return_value:
                    return obj
            LOGGER.debug("Waiting {:.2f} seconds before retrying".format(
                self.interval))
            sleep(self.interval)
        raise PollingTimeoutError


class BooleanCallablePoller(PollerBase):
    """A poller that selects objects based on the boolean return value of one
    its methods."""
    @staticmethod
    def _check_ready(obj, attribute, args=(), kwargs={}):
        """A readiness check that evaluates to True if the `attribute`
        method of the `obj` object returns boolean True when called with
        the provided args and kwargs."""
        return bool(getattr(obj, attribute)(*args, **kwargs))
