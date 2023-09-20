import logging

import modules.app

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
    # logging.disable(logging.CRITICAL)

    logging.debug('program begins.')
    modules.app.App().run()
    logging.debug('program ends.')
