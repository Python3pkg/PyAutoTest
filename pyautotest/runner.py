import logging
import os.path
import subprocess
from pyautotest import importutil

log = logging.getLogger(__name__)

def from_config(config):
    """
    >>> c = {'test_runner_name': 'file'}
    >>> from_config(c) # doctest: +ELLIPSIS
    <class 'runner.FileTestRunner'>

    >>> from_config({})
    Traceback (most recent call last):
        ...
    ValueError: Unknown Test Runner: None
    """
    if config.get('test_runner_module'):
        mod = importutil.import_module(config['test_runner_module'])
        return mod.get_runner()

    name = config.get('test_runner_name')
    if name not in test_runner_map:
        raise ValueError("Unknown Test Runner: %s" % name)
    return test_runner_map[name]


class FileTestRunner(object):
    """A test runner which runs a test file using `command`.
    """
    default_command = ['python']

    def __init__(self, file_filter, test_mapper, command=None):
        self.file_filter        = file_filter
        self.test_mapper        = test_mapper
        self.command            = command or ['python']

    def run(self, filename):
        if not self.file_filter.should_test(filename):
            log.info("Ignoring not testable file: %s", filename)
            return

        test_filename = self.test_mapper.get_test_filename(filename)
        if not os.path.isfile(test_filename):
            log.warn("Missing test for %s. Expected at %s",
                filename, test_filename)
            return

        test_name = self.get_test_name(test_filename)
        self.run_test(test_name)

    def run_test(self, test_name):
        subprocess.call(self.command + [test_name])

    def get_test_name(self, filename):
        return filename


class ModuleRunner(FileTestRunner):
    default_command = ['python', '-m', 'unittest']

    def get_test_name(self, filename):
        return '.'.join(filename.split(os.path.sep))[:-len('.py')]


class TestifyRunner(ModuleRunner):
    default_command = ['testify', '-v', '--summary']


class UnitTest2Runner(ModuleRunner):
    default_command = ['unit2', '-v',]


class DocTestRunner(FileTestRunner):
    default_command = ['python', '-m', 'doctest']


class PyTestRunner(FileTestRunner):
    default_command = ['py.test']


test_runner_map = {
    'file':         FileTestRunner,
    'unittest':     ModuleRunner,
    'doctest':      DocTestRunner,
    'testify':      TestifyRunner,
    'unittest2':    UnitTest2Runner,
    'pytest':       PyTestRunner
}
