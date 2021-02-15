"""
    Copyright 2021 Walter Pachlinger (walter.pachlinger@gmail.com)

    Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European
    Commission - subsequent versions of the EUPL (the LICENSE). You may not use this work except
    in compliance with the LICENSE. You may obtain a copy of the LICENSE at:

        https://joinup.ec.europa.eu/software/page/eupl

    Unless required by applicable law or agreed to in writing, software distributed under the
    LICENSE is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
    either express or implied. See the LICENSE for the specific language governing permissions
    and limitations under the LICENSE.
"""
import os
import sys
import json
from typing import Any
import logging.config
import signal
import time
import iot_runtime

class ConfigFile:
    """ Wrapper for the local configuration file. Maybe this should be moved to "wp_util".
        Looks for a file with the same name as the script, with extension .config.json in
        the current application directory, if no file name is given.

    Attributes:
        _config : dict
            The dictionary created by loading the JSON configuration file.

    Methods:
        ConfigFile:
            Constructor.
        contains : bool
            Checks whether or not a configuration item is present in the settings file.
        __getitem__ : Any
            Accessor for an element of the configuration dictionary.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, config_file_path: str = None):
        """ Constructor.

        Parameters:
            config_file_path : str, optional
                Full path name of the configuration file.
        """
        if config_file_path is None:
            conf_file_name = f"{os.path.splitext(os.path.basename(__file__))[0]}.config.json"
        else:
            conf_file_name = config_file_path
        with open(conf_file_name) as json_file:
            self._config = json.load(json_file)

    def __getitem__(self, item_name: str) -> Any:
        """ Accessor for an element of the configuration dictionary. """
        return self._config[item_name]

    def contains(self, item_name: str) -> bool:
        """ Checks whether or not a configuration item is present in the settings file. """
        return item_name in self._config

class ExitSignal:
    """ Wrapper for the indication of a handled SIGTERM or SIGINT signal. """
    def __init__(self):
        """ Constructor. """
        self._value = False

    @property
    def is_set(self) -> bool:
        """ Checks if a signal has been handled """
        return self._value

    def set(self) -> None:
        """ Reports a handled signal. """
        self._value = True

exit_signal = ExitSignal()

def handle_signal(sig, frm):
    """ Handle a signal by setting the ExitSignal. """
    # pylint: disable=unused-argument
    exit_signal.set()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        settings = ConfigFile(sys.argv[1])
    else:
        settings = ConfigFile()
    iot_hosts = []
    if settings.contains('logging'):
        logging.config.dictConfig(settings['logging'])
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    for process_group in settings['process_groups']:
        iot_hosts.append(iot_runtime.iot_host.IotHost(settings['config_db_path'], process_group))
    for iot_host in iot_hosts:
        iot_host.start_agents()
        if settings.contains('statistics_db_path'):
            iot_host.start_data_recording(settings['statistics_db_path'])
    while not exit_signal.is_set:
        time.sleep(1)
    for iot_host in iot_hosts:
        iot_host.stop_agents()
