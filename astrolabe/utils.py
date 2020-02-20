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

from collections import defaultdict
import json
import logging
import os
from time import monotonic

import click
import junitparser


class ClickLogHandler(logging.Handler):
    """Handler for print log statements via Click's echo functionality."""
    def emit(self, record):
        try:
            msg = self.format(record)
            use_stderr = False
            if record.levelno >= logging.WARNING:
                use_stderr = True
            click.echo(msg, err=use_stderr)
        except Exception:
            self.handleError(record)


def assert_subset(dict1, dict2):
    """Utility that asserts that `dict2` is a subset of `dict1`, while
    accounting for nested fields."""
    for key, value in dict2.items():
        if key not in dict1:
            raise AssertionError("not a subset")
        if isinstance(value, dict):
            assert_subset(dict1[key], value)
        else:
            assert dict1[key] == value


class Timer:
    """Class to simplify timing operations."""
    def __init__(self):
        self._start = None
        self._end = None

    def reset(self):
        self.__init__()

    def start(self):
        self._start = monotonic()
        self._end = None

    def stop(self):
        self._end = monotonic()

    @property
    def elapsed(self):
        if self._end is None:
            return monotonic() - self._start
        return self._end - self._start


def cached_property(func):
    """Decorator to memoize a class method that accepts no args/kwargs."""
    memo = None

    def memoized_function(self, *args, **kwargs):
        if args or kwargs:
            raise RuntimeError("cannot memoize methods that accept arguments")
        nonlocal memo
        if memo is None:
            memo = func(self)
        return memo

    return memoized_function


def encode_cdata(data):
    """Encode `data` to XML-recognized CDATA."""
    return "<![CDATA[{data}]]>".format(data=data)


class SingleTestXUnitLogger:
    def __init__(self, *, output_directory):
        self._output_directory = os.path.realpath(os.path.join(
            os.getcwd(), output_directory))

        # Ensure folder exists.
        try:
            os.mkdir(self._output_directory)
        except FileExistsError:
            pass

    def write_xml(self, test_case, filename):
        filename += '.xml'
        xml_path = os.path.join(self._output_directory, filename)

        # Remove existing file if applicable.
        try:
            os.unlink(xml_path)
        except FileNotFoundError:
            pass

        # use filename as suitename
        suite = junitparser.TestSuite(filename)
        suite.add_testcase(test_case)

        xml = junitparser.JUnitXml()
        xml.add_testsuite(suite)
        xml.write(xml_path)


def _nested_defaultdict():
    """An infinitely nested defaultdict type."""
    return defaultdict(_nested_defaultdict)


def _merge_dictionaries(dicts):
    """Utility method to merge a list of dictionaries.
    Last observed value prevails."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


class _JsonDotNotationType(click.ParamType):
    """Custom Click-type for user-friendly JSON input."""
    def convert(self, value, param, ctx):
        # Return None and target type without change.
        if value is None or isinstance(value, dict):
            return value

        # Parse the input (of type path.to.namespace=value).
        ns, config_value = value.split("=")
        ns_path = ns.split(".")
        return_value = _nested_defaultdict()

        # Construct dictionary from parsed option.
        pointer = return_value
        for key in ns_path:
            if key == ns_path[-1]:
                pointer[key] = config_value
            else:
                pointer = pointer[key]

        # Convert nested defaultdict into vanilla dictionary.
        return json.loads(json.dumps(return_value))
