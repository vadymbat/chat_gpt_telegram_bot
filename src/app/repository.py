from app.model import BotUsers
import logging

logger = logging.getLogger()


class BotUsersRepository:
    def __init__(self) -> None:
        self._model = BotUsers

    def add(self, user_id: int) -> None:
        user = self._model(hash_key=user_id)
        user.save()
        logger.info(f"Added authorized user '{user_id}'.")

    def remove(self, user_id: int):
        self._model(hash_key=user_id).delete()
        logger.info(f"Removed user '{user_id}'.")

    def exists(self, user_id: int) -> bool:
        try:
            self._model.get(hash_key=user_id)
            return True
        except self._model.DoesNotExist:
            return False
