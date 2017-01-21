import daemon
import logging
import configparser
from nzbandwidth import monitor


if __name__ == '__main__':

    # Get configurations
    Config = configparser.ConfigParser()
    Config.read('config.ini')
    log_file = open(Config.get('nzbandwidth', 'log_file'), 'w')
    log_level = Config.get('nzbandwidth', 'log_level')
    daemon_mode = Config.get('nzbandwidth', 'daemon')

    if Config.get('nzbandwidth', 'log_level') == 'info':
        log_level = logging.INFO
    elif Config.get('nzbandwidth', 'log_level') == 'debug':
        log_level = logging.DEBUG

    # Setup Logging
    logging.basicConfig(filename=Config.get('nzbandwidth', 'log_file'),
                        format='[%(asctime)s][%(levelname)s]: %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=log_level)

    if daemon_mode == 'true':
        context = daemon.DaemonContext(working_directory='/Users/rickygrassmuck/Development',
                                       umask=0o002)

        with context:
            monitor(Config, logging)

    else:
        try:
            monitor(Config)
        except KeyboardInterrupt:
            logging.info("Stopping service")
