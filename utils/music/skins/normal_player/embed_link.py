# -*- coding: utf-8 -*-
import datetime
import re
from os.path import basename

import disnake

from utils.music.converters import time_format, fix_characters, get_button_style
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls

class EmbedLinkSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://media.discordapp.net/attachments/1162795987014787162/1221122341464047616/image.png?ex=66116dcd&is=65fef8cd&hm=0cf0bcf28b2039942719cce1b9335ae7e13871d865047ae142cad306aea1896b&=&format=webp&quality=lossless&width=316&height=437"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = True
        player.auto_update = 0
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": []
        }

        txt = ""

        if player.current_hint:
            txt += f"> `<:tec_bulb:1216393991780831273>` **Hint:** `{player.current_hint}`"

        if player.current.is_stream:
            duration_txt = f"\n> `<:tec_live:1216397982602231859>` **⠂Duration:** `Livestream`"
        else:
            duration_txt = f"\n> `<a:tec_uptime:1213851690814668900>` **⠂Duration:** `{time_format(player.current.duration)}`"

        title = f"`{player.current.title}`" if not player.current.uri else f"[`{fix_characters(player.current.title, 40)}`]({player.current.uri})"

        if player.paused:
            txt += f"\n> `<:tec_pause:1213808106727800862>` **⠂Paused:** {title}{duration_txt}"

        else:
            txt += f"\n> `<:tec_play:1213064302647320626>` **⠂Playing Now:** {title}{duration_txt}"
            if not player.current.is_stream:
                txt += f" `[`<t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=player.current.duration - player.position)).timestamp())}:R>`]`" \
                if not player.paused else ''

        if q:=len(player.queue):
            txt += f" `[In Queue: {q}]`"

        if not player.current.autoplay:
            txt += f" <@{player.current.requester}>\n"
        else:
            try:
                txt += f" [`[Recommended Music]`](<{player.current.info['extra']['related']['uri']}>)"
            except:
                txt += " `[Recommended Music]`"

        if player.command_log:

            log = re.sub(r"\[(.+)]\(.+\)", r"\1", player.command_log.replace("`", "")) # Remove links from command_log to avoid generating more than one preview.

            txt += f"> {player.command_log_emoji} **⠂Last Interaction:** {log}\n"

        data["content"] = txt

        data["components"] = [
            disnake.ui.Button(emoji="<:tec_PlayPause:1216414413922504794>", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="<:tec_rewind:1216401126690132190>", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="<:tec_stop:1216409401217515550>", custom_id=PlayerControls.stop),
            disnake.ui.Button(emoji="<:tec_for:1216405564150517780>", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:tec_queue:1217105407038722108>", custom_id=PlayerControls.queue, disabled=not (player.queue or player.queue_autoplay)),
            disnake.ui.Select(
                placeholder="More options:",
                custom_id="musicplayer_dropdown_inter",
                min_values=0, max_values=1,
                options=[
                    disnake.SelectOption(
                        label="Add music", emoji="<:tec_add:1216398582609874996>",
                        value=PlayerControls.add_song,
                        description="Add a song/playlist to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add favorite to queue", emoji="<:tec_star:1212069288203255948>",
                        value=PlayerControls.enqueue_fav,
                        description="Add one of your favorites to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add to your favorites", emoji="<:tec_heart:1216398247535316993>",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Play from start", emoji="<:tec_rewind:1216401126690132190>",
                        value=PlayerControls.seek_to_start,
                        description="Go back to the beginning of the current song."
                    ),
                    disnake.SelectOption(
                        label=f"Volume: {player.volume}%", emoji="<:tec_vol:1215664974622625902>",
                        value=PlayerControls.volume,
                        description="Adjust volume."
                    ),
                    disnake.SelectOption(
                        label="Shuffle", emoji="<:tec_shuffle:1216409744978350080>",
                        value=PlayerControls.shuffle,
                        description="Shuffle the songs in the queue."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="<a:tec_music:1216415601778495558>",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Loop", emoji="<a:tec_loop1:1216407116584325241>",
                        value=PlayerControls.loop_mode,
                        description="Toggle song/queue looping."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="<a:tec_moon:1220632480340508735>",
                        value=PlayerControls.nightcore,
                        description="Effect that increases the speed and pitch of the music."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="<a:tec_reload:1214591681073254410>",
                        value=PlayerControls.autoplay,
                        description="System for automatic music addition when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label= ("Disable" if player.restrict_mode else "Enable") + " restricted mode", emoji="<a:tec_lock:1213021806697648128>",
                        value=PlayerControls.restrict_mode,
                        description="Only DJ's/Staff can use restricted commands."
                    ),
                ]
            ),
        ]

        if player.current.ytid and player.node.lyric_support:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= "View lyrics", emoji="<:tec_page:1214593594078527499>",
                    value=PlayerControls.lyrics,
                    description="Get lyrics of current music."
                )
            )


        if isinstance(player.last_channel, disnake.VoiceChannel):
            txt = "Disable" if player.stage_title_event else "Enable"
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= f"{txt} automatic status", emoji="<:tec_speaker:1221118288889778349>",
                    value=PlayerControls.stage_announce,
                    description=f"{txt} automatic status of the voice channel."
                )
            )

        if not player.static and not player.has_thread:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Song-Request Thread", emoji="<:tec_speech:1215664691175497760>",
                    value=PlayerControls.song_request_thread,
                    description="Create a temporary thread/chat to request songs using just the name/link."
                )
            )

        return data

def load():
    return EmbedLinkSkin()
