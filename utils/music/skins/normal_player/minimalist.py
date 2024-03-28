# -*- coding: utf-8 -*-
from os.path import basename

from utils.music.converters import fix_characters, time_format
from utils.music.models import LavalinkPlayer


class Minimalist:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1221119584296370296/image.png?ex=66116b3c&is=65fef63c&hm=2e55d8236bfc03a6aa45b638c0343b4f3541f54800bbf1201020cecc422a09d8&"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = False
        player.auto_update = 0
        player.hint_rate = 9
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        duration = "<:tec_live:1216397982602231859> Livestream" if player.current.is_stream else \
            time_format(player.current.duration)

        data = {
            "embeds": [],
            "content": f"<a:tec_play:1213064036606943254>`⠂Currently playing:` [`{fix_characters(player.current.title, 30)}`](<{player.current.uri or player.current.search_uri}>) `[{fix_characters(player.current.author, 20)}] {duration}`"
        }

        if player.current_hint:
            data["content"] += f"\n`<:tec_bulb:1216393991780831273>⠂Hint: {player.current_hint}`"

        return data

def load():
    return Minimalist()
