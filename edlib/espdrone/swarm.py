# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
from threading import Thread

from edlib.espdrone import Espdrone
from edlib.espdrone.syncEspdrone import SyncEspdrone


class _Factory:
    """
    Default Espdrone factory class.
    """

    def construct(self, uri):
        return SyncEspdrone(uri)


class CachededFactory:
    """
    Factory class that creates Espdrone instances with TOC caching
    to reduce connection time.
    """

    def __init__(self, ro_cache=None, rw_cache=None):
        self.ro_cache = ro_cache
        self.rw_cache = rw_cache

    def construct(self, uri):
        ed = Espdrone(ro_cache=self.ro_cache, rw_cache=self.rw_cache)
        return SyncEspdrone(uri, ed=ed)


class Swarm:
    """
    Runs a swarm of Espdrones. It implements a functional-ish style of
    sequential or parallel actions on all individuals of the swarm.

    When the swarm is connected, a link is opened to each Espdrone through
    SyncEspdrone instances. The instances are maintained by the class and are
    passed in as the first argument in swarm wide actions.
    """

    def __init__(self, uris, factory=_Factory()):
        """
        Constructs a Swarm instance and instances used to connect to the
        Espdrones

        :param uris: A set of uris to use when connecting to the Espdrones in
        the swarm
        :param factory: A factory class used to create the instances that are
         used to open links to the Espdrones. Mainly used for unit testing.
        """
        self._eds = {}
        self._is_open = False

        for uri in uris:
            self._eds[uri] = factory.construct(uri)

    def open_links(self):
        """
        Open links to all individuals in the swarm
        """
        if self._is_open:
            raise Exception('Already opened')

        try:
            self.parallel_safe(lambda sed: sed.open_link())
            self._is_open = True
        except Exception as e:
            self.close_links()
            raise e

    def close_links(self):
        """
        Close all open links
        """
        for uri, ed in self._eds.items():
            ed.close_link()

        self._is_open = False

    def __enter__(self):
        self.open_links()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_links()

    def sequential(self, func, args_dict=None):
        """
        Execute a function for all Espdrones in the swarm, in sequence.

        The first argument of the function that is passed in will be a
        SyncEspdrone instance connected to the Espdrone to operate on.
        A list of optional parameters (per Espdrone) may follow defined by
        the args_dict. The dictionary is keyed on URI.

        Example:
        def my_function(sed, optional_param0, optional_param1)
            ...

        args_dict = {
            URI0: [optional_param0_ed0, optional_param1_ed0],
            URI1: [optional_param0_ed1, optional_param1_ed1],
            ...
        }


        self.sequential(my_function, args_dict)

        :param func: the function to execute
        :param args_dict: parameters to pass to the function
        """
        for uri, ed in self._eds.items():
            args = self._process_args_dict(ed, uri, args_dict)
            func(*args)

    def parallel(self, func, args_dict=None):
        """
        Execute a function for all Espdrones in the swarm, in parallel.
        One thread per Espdrone is started to execute the function. The
        threads are joined at the end. Exceptions raised by the threads are
        ignored.

        For a description of the arguments, see sequential()

        :param func:
        :param args_dict:
        """
        try:
            self.parallel_safe(func, args_dict)
        except Exception:
            pass

    def parallel_safe(self, func, args_dict=None):
        """
        Execute a function for all Espdrones in the swarm, in parallel.
        One thread per Espdrone is started to execute the function. The
        threads are joined at the end and if one or more of the threads raised
        an exception this function will also raise an exception.

        For a description of the arguments, see sequential()

        :param func:
        :param args_dict:
        """
        threads = []
        reporter = self.Reporter()

        for uri, sed in self._eds.items():
            args = [func, reporter] + \
                self._process_args_dict(sed, uri, args_dict)

            thread = Thread(target=self._thread_function_wrapper, args=args)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        if reporter.is_error_reported():
            raise Exception('One or more threads raised an exception when '
                            'executing parallel task')

    def _thread_function_wrapper(self, *args):
        try:
            func = args[0]
            reporter = args[1]
            func(*args[2:])
        except Exception:
            reporter.report_error()

    def _process_args_dict(self, sed, uri, args_dict):
        args = [sed]

        if args_dict:
            args += args_dict[uri]

        return args

    class Reporter:

        def __init__(self):
            self.error_reported = False

        def report_error(self):
            self.error_reported = True

        def is_error_reported(self):
            return self.error_reported
