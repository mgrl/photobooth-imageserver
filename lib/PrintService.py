from queue import Queue
import logging
logger = logging.getLogger(__name__)


class PrintService():
    """Handles printer actions"""

    def __init__(self, cs, ee):
        self._cs = cs
        self._ee = ee

        self._print_queue = Queue(1)

        self._ee.on("print/picture", self.on_print)

    def on_print(self, id):
        logger.debug(f"print file '{id}' requested")
        self._print_queue.put_nowait(id)

    def _print(self):
        logger.debug(f"getting file off the queue only if printer idle")
        # if printer idle=queue.get and print.
        # if config==add qr code: do it
        # if config==add text: do it
        logger.info(
            f"printing file to printer xxx via cmd in thread in blocking way")
