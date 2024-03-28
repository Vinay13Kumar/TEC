# -*- coding: utf-8 -*-
import itertools
from os.path import basename

import disnake

from utils.music.converters import time_format, fix_characters, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls

class MiniSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1221114179390275594/image.png?ex=66116633&is=65fef133&hm=55e7f2f0501cfe92c79c5a60f041621ba25ecc479c518af6163497d68b59248e&"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = True
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
            description=f"[`{player.current.single_title}`]({player.current.uri or player.current.search_uri})"
        )
        embed_queue = None
        queue_size = len(player.queue)

        if not player.paused:
            embed.set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"]),
            )

        else:
            embed.set_author(
                name="Paused:",
                icon_url="https://cdn.discordapp.com/emojis/1213808106727800862.webp?size=128&quality=lossless"
            )

        if player.current.track_loops:
            embed.description += f" `[<a:tec_reload:1214591681073254410> {player.current.track_loops}]`"

        elif player.loop:
            if player.loop == 'current':
                embed.description += ' `[<a:tec_reload:1214591681073254410> current track]`'
            else:
                embed.description += ' `[<:tec_Loop:1216406941191114793> queue]`'

        if not player.current.autoplay:
            embed.description += f" `[`<@{player.current.requester}>`]`"
        else:
            try:
                embed.description += f" [`[Recommended]`]({player.current.info['extra']['related']['uri']})"
            except:
                embed.description += "` [Recommended]`"

        duration = "<:tec_live:1216397982602231859> Livestream" if player.current.is_stream else \
            time_format(player.current.duration)

        embed.add_field(name="<a:tec_uptime:1213851690814668900> **⠂Duration:**", value=f"```ansi\n[34;1m{duration}[0m\n```")
        embed.add_field(name="<a:tec_dot:1216394673896030289> **⠂Uploader/Artist:**",
                        value=f"```ansi\n[34;1m{fix_characters(player.current.author, 18)}[0m\n```")

        if player.command_log:
            embed.add_field(name=f"{player.command_log_emoji} **⠂Last Interaction:**",
                            value=f"{player.command_log}", inline=False)

        if queue_size:

            embed.description += f" `({queue_size})`"

            if player.mini_queue_enabled:
                embed_queue = disnake.Embed(
                    color=embed_color,
                    description="\n".join(
                        f"`{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '<:tec_live:1216397982602231859> Livestream'}]` [`{fix_characters(t.title, 38)}`]({t.uri})"
                        for n, t in (enumerate(itertools.islice(player.queue, 5)))
                    )
                )
                embed_queue.set_image(url="https://media.discordapp.net/attachments/1162795987014787162/1203207132812546078/mjD6IaM.webp?ex=6610da76&is=65fe6576&hm=5a514fd0f39ac1c610c6bfbf7b98d37ed6bc233d89f21e933ce636df5abd2a9e&=&format=webp&width=1281&height=9")

        embed.set_thumbnail(url=player.current.thumb)
        embed.set_image(url="https://media.discordapp.net/attachments/1162795987014787162/1203207132812546078/mjD6IaM.webp?ex=6610da76&is=65fe6576&hm=5a514fd0f39ac1c610c6bfbf7b98d37ed6bc233d89f21e933ce636df5abd2a9e&=&format=webp&width=1281&height=9")

        if player.current_hint:
            embed.set_footer(text=f"<:tec_bulb:1216393991780831273> Hint: {player.current_hint}")

        data["embeds"] = [embed_queue, embed] if embed_queue else [embed]

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
                        label="Add song", emoji="<:tec_add:1216398582609874996>",
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
                        description="Move the current song's time to the start."
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
                        label="Re-add", emoji="<a:tec_play:1213064036606943254>",
                        value=PlayerControls.readd,
                        description="Re-add the played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Loop", emoji="<:tec_Loop:1216406941191114793>",
                        value=PlayerControls.loop_mode,
                        description="Activate/Deactivate song/queue looping."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="<a:tec_moon:1220632480340508735>",
                        value=PlayerControls.nightcore,
                        description="Effect that increases the speed and pitch of the song."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="<a:tec_reload:1214591681073254410>",
                        value=PlayerControls.autoplay,
                        description="System to automatically add music when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label= ("Disable" if player.restrict_mode else "Enable") + " restrict mode", emoji="<a:tec_lock:1213021806697648128>",
                        value=PlayerControls.restrict_mode,
                        description="Only DJs/Staff can use restricted commands."
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
                    label="Player's Mini-queue", emoji="<:tec_queue:1217105407038722108>",
                    value=PlayerControls.miniqueue,
                    description="Activate/Deactivate the player's mini-queue."
                )
            )

        if isinstance(player.last_channel, disnake.VoiceChannel):
            txt = "Disable" if player.stage_title_event else "Activate"
            data["components"][5].options.append(
                disnake.SelectOption(
                    label= f"{txt} automatic status", emoji="<:tec_speaker:1221118288889778349>",
                    value=PlayerControls.stage_announce,
                    description=f"{txt} automatic status in the voice channel."
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
    return MiniSkin()
