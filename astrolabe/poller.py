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

from time import sleep

from astrolabe.exceptions import PollingTimeoutError
from astrolabe.utils import Timer


class SelectBase:
    def __init__(self, *, frequency, timeout):
        self.interval = 1.0 / frequency
        self.timeout = timeout

    @staticmethod
    def poll(obj, attribute, args, kwargs):
        raise NotImplementedError

    def select(self, objects, *, attribute, args, kwargs):
        timer = Timer()
        timer.start()
        while timer.elapsed < self.timeout:
            for obj in objects:
                return_value = self.poll(obj, attribute, args, kwargs)
                if return_value:
                    return obj
            sleep(self.interval)
        raise PollingTimeoutError


class BooleanCallableSelector(SelectBase):
    @staticmethod
    def poll(obj, attribute, args=(), kwargs={}):
        return bool(getattr(obj, attribute)(*args, **kwargs))
