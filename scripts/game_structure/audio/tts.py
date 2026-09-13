from html.parser import HTMLParser
import logging
from typing import Optional

from pygame_gui.elements import UIButton, UILabel, UITextBox
import pyttsx3

from scripts.cat.cats import Cat
from scripts.game_structure.game.settings import game_setting_get, game_setting_set
from scripts.game_structure.monkeypatch import translate
from scripts.ui.elements.cat_button import CatButton
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.id_image_button import IDImageButton
from scripts.ui.elements.save_button import UISaveButton
from scripts.ui.elements.sprite_button import UISpriteButton

logger = logging.getLogger(__name__)

class TTSParser(HTMLParser):
    def __init__(self, *kwargs):
        self.text = []
        super().__init__(*kwargs)

    def handle_data(self, data):
        self.text.append(data)

    def flush_text(self):
        result = "".join(self.text)
        self.text = []
        return result

parser = TTSParser()

class TTS:
    def __init__(self):
        try:
            self.engine: Optional[pyttsx3.Engine] = pyttsx3.init(debug=True)

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

        if not self.engine._inLoop:
            self.engine.startLoop()

        self.engine.isBusy()

    def say_next(self):
        """
        Says the next queued text in the TTS engine.
        """
        if self.engine is None:
            return

        if not self.engine._inLoop:
            self.engine.startLoop()

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

    def handle_tts_events(self, event, hovered_element):
        """
        TODO: docs

        Call i18n to perform the translation, but this isn't perfect when the buttons
        are represented by icons or contain special characters. This would be resolved
        by alt text, but i18n makes this more complicated.
        """
        if self.engine is None or hovered_element is None:
            return

        # The order and elifs matter, because isinstance checks subclasses.
        if isinstance(hovered_element, UISpriteButton):
            if (cat_object := hovered_element.return_cat_object()) is not None:
                self.engine.say(str(cat_object.name))
            elif (cat_id := hovered_element.return_cat_id()) is not None:
                if (cat := Cat.all_cats.get(cat_id)) is not None:
                    self.engine.say(str(cat.name))
        elif isinstance(hovered_element, CatButton):
            if hovered_element.text:
                self.engine.say(translate(hovered_element.text, **hovered_element.text_kwargs))
            elif (cat_id := hovered_element.return_cat_id()) is not None:
                self.engine.say(cat_id)
            elif (cat_object := hovered_element.return_cat_object()) is not None:
                self.engine.say(str(cat_object.name))
        elif isinstance(hovered_element, UICheckbox):
            self.engine.say(translate(hovered_element.tool_tip_text, **hovered_element.tool_tip_text_kwargs))
        elif isinstance(hovered_element, IDImageButton):
            self.engine.say("Involved cats")
        elif isinstance(hovered_element, UIButton) or isinstance(hovered_element, UILabel):
            if hovered_element.text:
                self.engine.say(translate(hovered_element.text, **hovered_element.text_kwargs))
            elif hovered_element.tool_tip_text:
                self.engine.say(translate(hovered_element.tool_tip_text, **hovered_element.tool_tip_text_kwargs))
        elif isinstance(hovered_element, UITextBox):
            # Feed it to a custom HTML parser to strip all formatting
            feed_input = translate(hovered_element.html_text, **hovered_element.text_kwargs)
            parser.feed(feed_input)
            output = parser.flush_text()
            self.engine.say(output)