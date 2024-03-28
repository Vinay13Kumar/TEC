# -*- coding: utf-8 -*-
import datetime
import itertools
from os.path import basename

import disnake

from utils.music.converters import fix_characters, time_format, get_button_style, music_source_image
from utils.music.models import LavalinkPlayer
from utils.others import PlayerControls


class DefaultSkin:

    __slots__ = ("name", "preview")

    def __init__(self):
        self.name = basename(__file__)[:-3]
        self.preview = "https://cdn.discordapp.com/attachments/1162795987014787162/1217108861065101413/3.png?ex=6602d3f5&is=65f05ef5&hm=ba6458aefaab805a6f2529c21c24858635c5b993a03b8bcb8584a96566b195c7&"

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

        embed = disnake.Embed(color=color)
        embed_queue = None
        vc_txt = ""

        if not player.paused:
            embed.set_author(
                name="Currently Playing:",
                icon_url=music_source_image(player.current.info["sourceName"])
            )

        else:
            embed.set_author(
                name="Paused:",
                icon_url="https://cdn.discordapp.com/emojis/1213808106727800862.webp?size=128&quality=lossless"
            )

        if player.current_hint:
            embed.set_footer(text=f"<:tec_bulb:1216393991780831273> Hint: {player.current_hint}")
        else:
            embed.set_footer(
                text=str(player),
                icon_url="https://i.ibb.co/QXtk5VB/neon-circle.gif"
            )

        player.mini_queue_feature = True

        duration = "> <:tec_live:1216397982602231859> **⠂** `Livestream`\n" if player.current.is_stream else \
            (f"> <a:tec_uptime:1213851690814668900> **⠂** `{time_format(player.current.duration)} [`" +
            f"<t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=player.current.duration - player.position)).timestamp())}:R>`]`\n"
            if not player.paused else '')

        txt = f"[`{player.current.single_title}`]({player.current.uri or player.current.search_uri})\n\n" \
              f"{duration}" \
              f"> <a:tec_user:1213060775795625984> **⠂** {player.current.authors_md}"

        if not player.current.autoplay:
            txt += f"\n> <:tec_hand:1216401473194295297> **⠂** <@{player.current.requester}>"
        else:
            try:
                mode = f" [`Recommended`]({player.current.info['extra']['related']['uri']})"
            except:
                mode = "`Recommended`"
            txt += f"\n> <:tec_heart:1216398247535316993> **⠂** {mode}"

        if player.current.track_loops:
            txt += f"\n> <a:tec_loop1:1216407116584325241> **⠂** `Remaining Loops: {player.current.track_loops}`"

        if player.loop:
            if player.loop == 'current':
                e = '<a:tec_loop1:1216407116584325241>'; m = 'Current Song'
            else:
                e = '<:tec_Loop:1216406941191114793>'; m = 'Queue'
            txt += f"\n> {e} **⠂** `Loop: {m}`"

        if player.current.album_name:
            txt += f"\n> <a:tec_disc:1213021509564764170> **⠂** [`{fix_characters(player.current.album_name, limit=36)}`]({player.current.album_url})"

        if player.current.playlist_name:
            txt += f"\n> <:tec_bookmark:1216397045741391974> **⠂** [`{fix_characters(player.current.playlist_name, limit=36)}`]({player.current.playlist_url})"

        if (qlenght:=len(player.queue)) and not player.mini_queue_enabled:
            txt += f"\n> <a:tec_play:1213064036606943254> **⠂** `{qlenght} song{'s'[:qlenght^1]} in queue`"

        if player.keep_connected:
            txt += "\n> <a:tec_loop1:1216407116584325241> **⠂** `24/7 Mode enabled`"

        txt += f"{vc_txt}\n"

        bar = "https://cdn.discordapp.com/attachments/554468640942981147/1127294696025227367/rainbow_bar3.gif"

        if player.command_log:
            txt += f"```ansi\n [34;1mLast Interaction[0m```**┕ {player.command_log_emoji} ⠂**{player.command_log}\n"

        if player.mini_queue_enabled:

            if len(player.queue):

                queue_txt = "\n".join(
                    f"`{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '<:tec_live:1216397982602231859> Livestream'}]` [`{fix_characters(t.title, 21)}`]({t.uri})"
                    for n, t in (enumerate(itertools.islice(player.queue, 3)))
                )

                embed_queue = disnake.Embed(title=f"Songs in queue: {qlenght}", color=color,
                                            description=f"\n{queue_txt}")

                if not player.loop and not player.keep_connected and not player.paused:

                    queue_duration = 0

                    for t in player.queue:
                        if not t.is_stream:
                            queue_duration += t.duration

                    embed_queue.description += f"\n`[<a:tec_clock:1217401304347840522> Songs end` <t:{int((disnake.utils.utcnow() + datetime.timedelta(milliseconds=(queue_duration + (player.current.duration if not player.current.is_stream else 0)) - player.position)).timestamp())}:R> `<a:tec_clock:1217401304347840522>]`"

                embed_queue.set_image(url=bar)

            elif len(player.queue_autoplay):
                queue_txt = "\n".join(
                    f"`<:tec_heart:1216398247535316993>⠂{(n + 1):02}) [{time_format(t.duration) if not t.is_stream else '<:tec_live:1216397982602231859> Livestream'}]` [`{fix_characters(t.title, 20)}`]({t.uri})"
                    for n, t in (enumerate(itertools.islice(player.queue_autoplay, 3)))
                )
                embed_queue = disnake.Embed(title="Next recommended songs:", color=color,
                                            description=f"\n{queue_txt}")
                embed_queue.set_image(url=bar)

        embed.description = txt
        embed.set_image(url=bar)
        embed.set_thumbnail(url=player.current.thumb)

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
                        label="Start from beginning", emoji="<:tec_rewind:1216401126690132190>",
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
                        description="Shuffle songs in the queue."
                    ),
                    disnake.SelectOption(
                        label="Re-add", emoji="<a:tec_play:1213064036606943254>",
                        value=PlayerControls.readd,
                        description="Re-add played songs back to the queue."
                    ),
                    disnake.SelectOption(
                        label="Loop", emoji="<:tec_Loop:1216406941191114793>",
                        value=PlayerControls.loop_mode,
                        description="Enable/Disable song/queue looping."
                    ),
                    disnake.SelectOption(
                        label=("Disable" if player.nightcore else "Enable") + " Nightcore effect", emoji="<a:tec_moon:1220632480340508735>",
                        value=PlayerControls.nightcore,
                        description="Effect that increases speed and pitch of the song."
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
                    label= "View lyrics", emoji="<:tec_bookmark:1216397045741391974>",
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
    return DefaultSkin()
