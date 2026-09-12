import logging
from typing import Optional

import pyttsx3

from scripts.game_structure.game.settings import game_setting_get, game_setting_set

logger = logging.getLogger(__name__)


class TTS:
    def __init__(self):
        try:
            self.engine: Optional[pyttsx3.Engine] = pyttsx3.init()

            # TODO: Use sound volume for now, but this could be its own setting.
            volume = game_setting_get("sound_volume") / 100
            self.engine.setProperty("volume", volume)

            self.engine.startLoop(False)
        except Exception as e:
            logger.exception("Failed to initialize TTS engine: %s", e)
            self.engine = None

    def get_busy(self):
        """
        Check if the engine is currently speaking.
        """
        if self.engine is None:
            return

        self.engine.isBusy()

    def queue_text(self, text):
        """
        Queues the given text to pass to the TTS engine.
        :param text: The text to read aloud
        """
        if self.engine is None:
            return

        self.engine.say(text)

    def say_next(self):
        """
        Says the next queued text in the TTS engine.
        """
        if self.engine is None:
            return

        self.engine.iterate()

    def change_volume(self, new_volume: int):
        """
        changes the volume
        :param new_volume: The new volume to set music to, int given should be between 0 and 100
        """
        # make sure given volume is between 0 and 100
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0

        # convert to a float and change volume accordingly
        self.volume = new_volume / 100
        game_setting_set("sound_volume", new_volume)
