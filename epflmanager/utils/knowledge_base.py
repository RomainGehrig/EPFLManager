import os
import pickle
import atexit

from ..settings import KNOWLEDGE_BASE_FILE
from ..utils import AliasList, get_logger

logger = get_logger(__name__)

class KnowledgeBase(object):
    def __init__(self, filename=None, save_on_delete=True):
        self._save_on_delete = save_on_delete

        alias = None

        if os.path.isfile(filename):
            logger.info("Knowledge base detected, will try to load")
            try:
                with open(filename, "rb") as f:
                    alias = pickle.load(f)

                logger.info("Knowledge base loaded")
            except:
                logger.error("Failed to load saved knowledge base, will create a new one")

        self._alias = alias if alias is not None else AliasList()
        self._filename = filename

        atexit.register(self._handle_exit)

    def add_entry(self, entry):
        self._alias.add_node(entry)

    def add_alias(self, alias, of):
        self._alias.add_and_merge(alias, of)

    def save(self):
        with open(self._filename, "wb") as f:
            pickle.dump(self._alias, f)
        logger.info("Knowledge base saved")

    def _handle_exit(self):
        if self._save_on_delete:
            logger.info("Knowledge base's `Save on delete` has triggered")
            self.save()

knowledge_base = KnowledgeBase(filename=KNOWLEDGE_BASE_FILE)
