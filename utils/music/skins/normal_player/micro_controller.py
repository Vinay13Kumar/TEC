# -*- coding: utf-8 -*-
from os.path import basename

import disnake

from utils.music.converters import fix_characters, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class MicroController:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1220638354727505921/image.png?ex=660fab0e&is=65fd360e&hm=34e56a7019df3b0dcd8a7723d8664f210465b7cf266ddcf6877e53778771f319&"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = True
        player.auto_update = 0
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": [],
        }

        embed_color = player.bot.get_color(player.guild.me)

        embed = disnake.Embed(
            color=embed_color,
            description=f"[`{fix_characters(player.current.single_title, 32)}`]({player.current.uri or player.current.search_uri}) "
                        f"[`{fix_characters(player.current.author, 12)}`] "
        )

        if not player.current.autoplay:
            embed.description += f"<@{player.current.requester}>"
        else:
            try:
                embed.description = f"[`[Recomendada]`]({player.current.info['extra']['related']['uri']})"
            except:
                embed.description = "`[Recomendada]`"

        embed.set_author(
            name="Currently Playing:",
            icon_url=music_source_image(player.current.info["sourceName"])
        )

        if player.command_log:
            embed.description += f"\n\n{player.command_log_emoji} ⠂**Last Interaction:** {player.command_log}"

        if player.current_hint:
            embed_hint = disnake.Embed(colour=embed_color)
            embed_hint.set_footer(text=f"<:tec_bulb:1216393991780831273> Hint: {player.current_hint}")
            data["embeds"].append(embed_hint)

        data["embeds"].append(embed)

        data["components"] = [
            disnake.ui.Button(emoji="<:tec_PlayPause:1216414413922504794>", label="Resume" if player.paused else "Pause", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="<:tec_prev:1216400464556462221>", label="Back", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="<:tec_stop:1216409401217515550>", label="Stop", custom_id=PlayerControls.stop, style=disnake.ButtonStyle.red),
            disnake.ui.Button(emoji="<:tec_next:1216400005972365345>", label="Skip", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:tec_queue:1217105407038722108>", label="Queue", custom_id=PlayerControls.queue,disabled=not (player.queue or player.queue_autoplay)),
            disnake.ui.Button(emoji="<:tec_heart:1216398247535316993>", label="Add to Favorites", custom_id=PlayerControls.add_favorite),
            disnake.ui.Button(emoji="<:tec_star:1212069288203255948>", label="Favorites", custom_id=PlayerControls.enqueue_fav),
        ]

        return data

def load():
    return MicroController()
