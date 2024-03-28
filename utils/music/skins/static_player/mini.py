# -*- coding: utf-8 -*-
import datetime
from os.path import basename

import disnake

from utils.music.converters import time_format, fix_characters, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class MiniStaticSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3] + "_static"
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1221142918602166427/image.png?ex=661180f7&is=65ff0bf7&hm=bd854d2056dc8c93374f5c129d79788d645d560568dfbe90dea39a5ca80e17e9&"

    def setup_features(self, player: LavalinkPlayer):
        player.mini_queue_feature = False
        player.controller_mode = True
        player.auto_update = 0
        player.hint_rate = player.bot.config["HINT_RATE"]
        player.static = True

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
            embed.description += f" `[<:tec_Loop:1216406941191114793> {player.current.track_loops}]`"

        elif player.loop:
            if player.loop == 'current':
                embed.description += ' `[<:tec_Loop:1216406941191114793> current song]`'
            else:
                embed.description += ' `[<a:tec_loop1:1216407116584325241> queue]`'

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

        embed.set_image(url=player.current.thumb or "https://media.discordapp.net/attachments/480195401543188483/987830071815471114/musicequalizer.gif")

        if queue_size:

            queue_txt = ""

            has_stream = False

            current_time = disnake.utils.utcnow() - datetime.timedelta(milliseconds=player.position) + datetime.timedelta(milliseconds=player.current.duration)

            queue_duration = 0

            for n, t in enumerate(player.queue):

                if t.is_stream:
                    has_stream = True

                elif n != 0:
                    queue_duration += t.duration

                if n > 7:
                    if has_stream:
                        break
                    continue

                if has_stream:
                    duration = time_format(t.duration) if not t.is_stream else '<:tec_live:1216397982602231859> Live'

                    queue_txt += f"`┌ {n + 1})` [`{fix_characters(t.title, limit=34)}`]({t.uri})\n" \
                                 f"`└ <a:tec_uptime:1213851690814668900> {duration}`" + (f" - `Repetitions: {t.track_loops}`" if t.track_loops else "") + \
                                 f" **|** `<:tec_hand:1216401473194295297>` <@{t.requester}>\n"

                else:
                    duration = f"<t:{int((current_time + datetime.timedelta(milliseconds=queue_duration)).timestamp())}:R>"

                    queue_txt += f"`┌ {n + 1})` [`{fix_characters(t.title, limit=34)}`]({t.uri})\n" \
                                 f"`└ <a:tec_uptime:1213851690814668900>` {duration}" + (f" - `Repetitions: {t.track_loops}`" if t.track_loops else "") + \
                                 f" **|** `<:tec_hand:1216401473194295297>` <@{t.requester}>\n"

            embed_queue = disnake.Embed(title=f"Songs in queue: {queue_size}",
                                        color=player.bot.get_color(player.guild.me),
                                        description=f"\n{queue_txt}")

            if not has_stream and not player.loop and not player.keep_connected and not player.paused and not player.current.is_stream:
                embed_queue.description += f"\n`[ <a:tec_clock:1217401304347840522> Songs end` <t:{int((current_time + datetime.timedelta(milliseconds=queue_duration + player.current.duration)).timestamp())}:R> `<a:tec_clock:1217401304347840522> ]`"

        elif player.queue_autoplay:

            queue_txt = ""

            has_stream = False

            current_time = disnake.utils.utcnow() - datetime.timedelta(milliseconds=player.position) + datetime.timedelta(milliseconds=player.current.duration)

            queue_duration = 0

            for n, t in enumerate(player.queue_autoplay):

                if t.is_stream:
                    has_stream = True

                elif n != 0:
                    queue_duration += t.duration

                if n > 7:
                    if has_stream:
                        break
                    continue

                if has_stream:
                    duration = time_format(t.duration) if not t.is_stream else '<:tec_live:1216397982602231859> Live'

                    queue_txt += f"`┌ {n + 1})` [`{fix_characters(t.title, limit=34)}`]({t.uri})\n" \
                                 f"`└ <a:tec_uptime:1213851690814668900> {duration}`" + (f" - `Repetitions: {t.track_loops}`" if t.track_loops else "") + \
                                 f" **|** `<:tec_heart:1216398247535316993>⠂Recommended`\n"

                else:
                    duration = f"<t:{int((current_time + datetime.timedelta(milliseconds=queue_duration)).timestamp())}:R>"

                    queue_txt += f"`┌ {n + 1})` [`{fix_characters(t.title, limit=34)}`]({t.uri})\n" \
                                 f"`└ <a:tec_uptime:1213851690814668900>` {duration}" + (f" - `Repetitions: {t.track_loops}`" if t.track_loops else "") + \
                                 f" **|** `<:tec_heart:1216398247535316993>⠂Recommended`\n"

            embed_queue = disnake.Embed(title="Next recommended songs:",
                                        color=player.bot.get_color(player.guild.me),
                                        description=f"\n{queue_txt}")

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
                        label="Add to favorites", emoji="<:tec_heart:1216398247535316993>",
                        value=PlayerControls.add_favorite,
                        description="Add the current song to your favorites."
                    ),
                    disnake.SelectOption(
                        label="Play from start", emoji="<:tec_rewind:1216401126690132190>",
                        value=PlayerControls.seek_to_start,
                        description="Go back to the beginning of the current song."
                    ),
                    disnake.SelectOption(
                        label=f"Volume: {player.volume}%", emoji="<a:tec_volu:1216405166459191428>",
                        value=PlayerControls.volume,
                        description="Adjust volume."
                    ),
                    disnake.SelectOption(
                        label="Shuffle", emoji="<:tec_shuffle:1216409744978350080>",
                        value=PlayerControls.shuffle,
                        description="Shuffle songs in the queue."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="<a:tec_music:1216415601778495558>",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Loop", emoji="<a:tec_loop1:1216407116584325241>",
                        value=PlayerControls.loop_mode,
                        description="Enable/Disable song/queue loop."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " nightcore effect", emoji="<a:tec_moon:1220632480340508735>",
                        value=PlayerControls.nightcore,
                        description="Effect that increases speed and pitch of the music."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.autoplay else "Enable") + " autoplay", emoji="<a:tec_reload:1214591681073254410>",
                        value=PlayerControls.autoplay,
                        description="System for automatic addition of music when the queue is empty."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.restrict_mode else "Enable") + " restrict mode", emoji="<a:tec_lock:1213021806697648128>",
                        value=PlayerControls.restrict_mode,
                        description="Only DJ/Staff can use restricted commands."
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
                    description="Create a temporary thread/conversation to request songs using just the name/link."
                )
            )

        return data

def load():
    return MiniStaticSkin()
