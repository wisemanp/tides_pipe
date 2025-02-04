# filepath: tides_pipe/modules/module.py
import logging
import os

class Module:
    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config
        self.done = False

    def set_logger(self, logger):
        self.logger = logger

    def set_done(self, status):
        self.done = status
        if self.done:
            self.write_done_file()

    def write_done_file(self):
        done_file = os.path.join(self.config['base_dir'], f"{self.__class__.__name__.lower()}_DONE.txt")
        with open(done_file, 'w') as f:
            f.write("TRUE\n")
        self.logger.info(f"{self.__class__.__name__} processing complete. Signaled with DONE.txt")