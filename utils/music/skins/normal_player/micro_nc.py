# -*- coding: utf-8 -*-
from os.path import basename

import disnake

from utils.music.converters import fix_characters
from utils.music.models import LavalinkPlayer


class MicroNC:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1221111456007983225/image.png?ex=661163aa&is=65feeeaa&hm=ab83c6ad2ae794dc7b5f020b642a005fdca1bec41f36fe52108f9e4380ea0b3e&"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = False
        player.auto_update = 0
        player.hint_rate = 9
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": []
        }

        embed = disnake.Embed(
            color=player.bot.get_color(player.guild.me),
            description=f"🎶 **⠂[{fix_characters(player.current.title, 30)}]({player.current.uri or player.current.search_uri})** `[{fix_characters(player.current.author, 12)}]`"
        )

        data["embeds"].append(embed)

        if player.current_hint:
            data["embeds"].append(disnake.Embed(color=player.bot.get_color(player.guild.me)).set_footer(text=f"<:tec_bulb:1216393991780831273> Hint: {player.current_hint}"))

        return data

def load():
    return MicroNC()
