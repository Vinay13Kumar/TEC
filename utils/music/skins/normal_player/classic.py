# -*- coding: utf-8 -*-
import itertools
from os.path import basename

import disnake

from utils.music.converters import fix_characters, time_format, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class ClassicSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://media.discordapp.net/attachments/1162795987014787162/1217108861065101413/3.png?ex=660c0e75&is=65f99975&hm=f670ae240b9d3c86d4df6c0e6d4d6486551b26e2aee568b0c37d41eeb450b12b&=&format=webp&quality=lossless&width=682&height=701"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = True
        player.controller_mode = True
        player.auto_update = 0
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = False

    def load(self, player: LavalinkPlayer) -> dict:

        data = {
            "content": None,
            "embeds": []
        }

        color = player.bot.get_color(player.guild.me)

        embed = disnake.Embed(color=color, description="")

        queue_txt = ""

        bar = "https://media.discordapp.net/attachments/1162795987014787162/1203207132812546078/mjD6IaM.webp?ex=6610da76&is=65fe6576&hm=5a514fd0f39ac1c610c6bfbf7b98d37ed6bc233d89f21e933ce636df5abd2a9e&=&format=webp&width=1281&height=96"

        embed_top = disnake.Embed(
            color=color,
            description=f"### [{player.current.title}]({player.current.uri or player.current.search_uri})"
        )
        embed.set_image(url=bar)

        embed_top.set_image(url=bar)

        embed_top.set_thumbnail(url=player.current.thumb)

        if not player.paused:
            (embed_top or embed).set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"])
            )
        else:
            (embed_top or embed).set_author(
                name="Paused:",
                icon_url="https://cdn.discordapp.com/emojis/1213808106727800862.webp?size=128&quality=lossless"
            )

        if player.current.is_stream:
            duration = "<:tec_live:1216397982602231859> **⠂ `Livestream`"
        else:
            duration = f"<a:tec_uptime:1213851690814668900> **⠂** `{time_format(player.current.duration)}`"

        txt = f"{duration}\n" \
              f"<a:tec_user:1213060775795625984> **⠂** `{player.current.author}`\n"

        if not player.current.autoplay:
            txt += f"<a:tec_listener:1213811291744116796> **⠂** <@{player.current.requester}>\n"
        else:
            try:
                mode = f" [`Recomendada`]({player.current.info['extra']['related']['uri']})"
            except:
                mode = "`Recomendada`"
            txt += f"> <:tec_heart:1216398247535316993> **⠂** {mode}\n"

        if player.current.playlist_name:
            txt += f"<:tec_bookmark:1216397045741391974> **⠂** [`{fix_characters(player.current.playlist_name, limit=19)}`]({player.current.playlist_url})\n"

        if qsize := len(player.queue):

            if not player.mini_queue_enabled:
                txt += f"<a:tec_music:1216415601778495558> **⠂** `{qsize} song{'s'[:qsize^1]} in queue`\n"
            else:
                queue_txt += "```ansi\n[0;33mUpcoming Songs:[0m```" + "\n".join(
                    f"`{(n + 1):02}) [{time_format(t.duration) if t.duration else '<:tec_live:1216397982602231859> Livestream'}]` "
                    f"[`{fix_characters(t.title, 29)}`]({t.uri})" for n, t in
                    enumerate(itertools.islice(player.queue, 3))
                )

                if qsize > 3:
                    queue_txt += f"\n`╚══════ And {(t:=qsize - 3)} more song{'s'[:t^1]} ══════╝`"

        elif len(player.queue_autoplay):
            queue_txt += "```ansi\n[0;33mNext song:[0m```" + "\n".join(
                f"`<:tec_heart:1216398247535316993>⠂{(n + 1):02}) [{time_format(t.duration) if t.duration else '<:tec_live:1216397982602231859> Livestream'}]` "
                f"[`{fix_characters(t.title, 29)}`]({t.uri})" for n, t in
                enumerate(itertools.islice(player.queue_autoplay, 3))
            )

        if player.command_log:
            txt += f"{player.command_log_emoji} **⠂Last Interaction:** {player.command_log}\n"

        embed.description += txt + queue_txt

        if player.current_hint:
            embed.set_footer(text=f"💡 Hint: {player.current_hint}")
        else:
            embed.set_footer(
                text=str(player),
                icon_url="https://i.ibb.co/QXtk5VB/neon-circle.gif"
            )

        data["embeds"] = [embed_top, embed] if embed_top else [embed]

        data["components"] = [
            disnake.ui.Button(emoji="<:tec_PlayPause:1216414413922504794>", custom_id=PlayerControls.pause_resume, style=get_button_style(player.paused)),
            disnake.ui.Button(emoji="<:tec_prev:1216400464556462221>", custom_id=PlayerControls.back),
            disnake.ui.Button(emoji="<:tec_stop:1216409401217515550>", custom_id=PlayerControls.stop),
            disnake.ui.Button(emoji="<:tec_next:1216400005972365345>", custom_id=PlayerControls.skip),
            disnake.ui.Button(emoji="<:tec_queue:1217105407038722108>", custom_id=PlayerControls.queue, disabled=not (player.queue or player.queue_autoplay)),
            disnake.ui.Select(
                placeholder="More options:",
                custom_id="musicplayer_dropdown_inter",
                min_values=0, max_values=1,
                options=[
                    disnake.SelectOption(
                        label="Add Song", emoji="<:tec_add:1216398582609874996>",
                        value=PlayerControls.add_song,
                        description="Add a song/playlist to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add Favorite to Queue", emoji="<:tec_star:1212069288203255948>",
                        value=PlayerControls.enqueue_fav,
                        description="Add one of your favorites to the queue."
                    ),
                    disnake.SelectOption(
                        label="Add to Your Favorites", emoji="<:tec_heart:1216398247535316993>",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Restart Song", emoji="<:tec_rewind:1216401126690132190>",
                        value=PlayerControls.seek_to_start,
                        description="Go back to the start of the current song."
                    ),
                    disnake.SelectOption(
                        label=f"Volume: {player.volume}%", emoji="<a:tec_volu:1216405166459191428>",
                        value=PlayerControls.volume,
                        description="Adjust volume."
                    ),
                    disnake.SelectOption(
                        label="Shuffle", emoji="<:tec_shuffle:1216409744978350080>",
                        value=PlayerControls.shuffle,
                        description="Shuffle the queue songs."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="<a:tec_music:1216415601778495558>",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Repeat", emoji="<:tec_Loop:1216406941191114793>",
                        value=PlayerControls.loop_mode,
                        description="Toggle song/queue repeat."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="🇳",
                        value=PlayerControls.nightcore,
                        description="Effect that increases the speed and pitch of the music."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="<a:tec_reload:1214591681073254410>",
                        value=PlayerControls.autoplay,
                        description="Automatically add music when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label= ("Disable" if player.restrict_mode else "Enable") + " restrict mode", emoji="<a:tec_lock:1213021806697648128>",
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


        if player.mini_queue_feature:
            data["components"][5].options.append(
                disnake.SelectOption(
                    label="Player Mini-queue", emoji="<:tec_queue:1217105407038722108>",
                    value=PlayerControls.miniqueue,
                    description="Toggle the player's mini-queue."
                )
            )

        if isinstance(player.last_channel, disnake.VoiceChannel):
            txt = "Disable" if player.stage_title_event else "Enable"
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= f"{txt} automatic status", emoji="<:tec_speaker:1221118288889778349>",
                    value=PlayerControls.stage_announce,
                    description=f"{txt} the automatic status of the voice channel."
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
    return ClassicSkin()
