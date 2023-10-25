"""
    @author     : casci
    @created    : Aug 28, 2022, 2:54 PM

    @description: Simple and lightweight wrapper implementation for Python's logging module.
"""

import logging
import traceback
import os


class Logger(object):
    def __init__(self):
        self._dir_loc = None
        self._tb = None
        self._current_level = None
        self.log_level = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
            'ERROR': logging.ERROR
        }
        self.log_format = '%(levelname)s%(message)s%(asctime)s'

    def _log(self, log_func, msg: str) -> None:
        """
        The generic private method to implement the custom log message.
        :param log_func: Log function handle, e.g. 'logging.info()'
        :param msg: str - Log message to be printed.
        :return: None
        """
        self._dir_loc = ''
        self._tb = traceback.extract_stack()

        if len(self._tb) > 2:
            self._dir_loc = r'{}'.format(os.path.basename(self._tb[-3][0])[:-3])

        log_message = r'{:^30}{:<14}{:<64}'.format(self._dir_loc, '', msg)
        log_func(log_message)

    def critical(self, msg: str) -> None:
        """
        Implements critical log.
        :param msg:  str - Log message to be printed.
        :return: None
        """
        self._log(logging.critical, msg)

    def warning(self, msg: str) -> None:
        """
        Implements warning log.
        :param msg:  str - Log message to be printed.
        :return: None
        """
        self._log(logging.warning, msg)

    def error(self, msg: str) -> None:
        """
        Implements error log.
        :param msg:  str - Log message to be printed.
        :return: None
        """
        self._log(logging.error, msg)

    def debug(self, msg: str) -> None:
        """
        Implements debug log.
        :param msg:  str - Log message to be printed.
        :return: None
        """
        self._log(logging.debug, msg)

    def info(self, msg: str) -> None:
        """
        Implements info log.
        :param msg:  str - Log message to be printed.
        :return: None
        """
        self._log(logging.info, msg)

    def init_log(self, level: str = 'DEBUG'):
        """
        Initializes the configuration for the logging wrapper.
        :param level: Logging module level.
        :return: None
        """
        if level not in self.log_level:
            print('Debug level not found. Setting it to DEBUG.')
            level = 'DEBUG'

        self._current_level = self.log_level[level]
        logging.basicConfig(level=self._current_level,
                            format=self.log_format,
                            datefmt='%Y-%m-%d %H:%M:%S')
