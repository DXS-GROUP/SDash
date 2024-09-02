import random
from warnings import warn
import aiohttp
import re

try:
    import youtube_dl
    import discord

    has_voice = True
except ImportError:
    has_voice = False

if has_voice:
    youtube_dl.utils.bug_reports_message = lambda: ""
    ytdl = youtube_dl.YoutubeDL(
        {
            "format": "bestaudio/best",
            "restrictfilenames": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "ignoreerrors": True,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "source_address": "0.0.0.0",
        }
    )


# ANCHOR Exceptions
class EmptyQueue(Exception):
    """Cannot skip because queue is empty"""


class NotConnectedToVoice(Exception):
    """Cannot create the player because bot is not connected to voice"""


class NotPlaying(Exception):
    """Cannot <do something> because nothing is being played"""


class YoutubeError(Exception):
    pass


# ANCHOR Song
class Song:
    def __init__(self, source: str, data: dict):
        self.source = source
        """The source of the song"""
        self.data = data
        """The data of the song which youtube_dl returns.

        .. tip::

            You can also access the data using ``Song.key`` and you don't need to use ``Song.data['key']``"""
        self.is_looping = False
        """Whether the song is looping"""

    def __getattribute__(self, __name: str):
        """Get the attribute from self or from self.data"""
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            try:
                return self.data[__name]
            except KeyError:
                raise AttributeError(
                    f"'{__name}' is not an attribute of {self} nor a key of {self.data}")


async def ytbettersearch(query):
    """This opens youtube.com and searches for the query, then returns the first result
    This is a workaround for youtube-dl's stupid search engine."""

    url = f"https://www.youtube.com/results?search_query={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
    regex = r"(?<=watch\?v=)\w+"
    v = re.search(regex, html).group()
    url = f"https://www.youtube.com/?v={v}"
    return url


def is_url(string):
    """This checks if `string` is a url or not"""
    if re.match(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        string,
    ):
        return True
    else:
        return False


async def get_video_data(self, query, bettersearch, loop) -> Song:
    """This gets the video data from youtube.com and returns it as a Song object

    Automatically gets called by :meth:`.MusicPlayer.queue` so you don't have to worry about this."""
    if not has_voice:
        raise RuntimeError(
            "disutils[voice] install needed in order to use voice")

    if not is_url(query) and not bettersearch:
        ytdl_ = youtube_dl.YoutubeDL(
            {
                "format": "bestaudio/best",
                "restrictfilenames": True,
                "noplaylist": True,
                "nocheckcertificate": True,
                "ignoreerrors": True,
                "logtostderr": False,
                "quiet": True,
                "no_warnings": True,
                "default_search": "auto",
                "source_address": "0.0.0.0",
            }
        )
        data = await loop.run_in_executor(
            None, lambda: ytdl_.extract_info(query, download=False)
        )
        try:
            data = data["entries"][0]
        except KeyError or TypeError:
            pass
        del ytdl_
    else:
        if not is_url(query) and bettersearch:
            url = await ytbettersearch(query)
        elif is_url(query):
            url = query
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        if data is None:
            raise YoutubeError()

    return Song(data["url"], data)


def _play_next(ctx, opts, music, after, loop):
    """This should not be called directly!"""
    if not has_voice:
        raise RuntimeError(
            "disutils[voice] install needed in order to use voice")

    try:
        player = music.get_player(ctx)
        queue = player._song_queue
        song = queue[0]
    except NotConnectedToVoice or IndexError:
        return

    if song.is_looping:
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(queue[0].source, **opts), player.volume)
        ctx.voice_client.play(
            source, after=lambda _e: after(ctx, opts, music, after, loop))
    else:
        try:
            queue.pop(0)
        except IndexError:
            player.stop()
            return

        if len(queue) > 0:
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(queue[0].source, **opts), player.volume)
            ctx.voice_client.play(
                source, after=lambda _e: after(ctx, opts, music, after, loop))


# ANCHOR Music
class Music:
    def __init__(self):
        if not has_voice:
            raise RuntimeError(
                "disutils[voice] install needed in order to use voice")
        self._players = []  # List of MusicPlayers

    def create_player(self, ctx):
        """This creates a new MusicPlayer. 

        .. versionchanged:: 1.4.5
            Gets automatically called by :meth:`get_player` if there's no MusicPlayer for the guild."""

        if not ctx.voice_client:
            raise NotConnectedToVoice(
                "Cannot create the player because bot is not connected to voice"
            )
        player = MusicPlayer(ctx, self)
        self._players.append(player)
        return player

    def get_player(self, ctx):
        """This gets the player from the ctx or creates a new one if there is none in that context"""
        for player in self._players:
            if player._voice_client.channel == ctx.voice_client.channel:
                return player
        return self.create_player(ctx)


# ANCHOR MusicPlayer
class MusicPlayer:
    def __init__(self, ctx, music: Music):
        if not has_voice:
            raise RuntimeError(
                "disutils[voice] install needed in order to use voice")
        self._ctx = ctx
        self._voice_client = ctx.voice_client
        self._loop = ctx.bot.loop
        self._bot = ctx.bot
        self._music = music
        self._song_queue = []
        self._after_func = _play_next
        self._volume = .5
        self._ffmpeg_options = {
            "options": "-vn -loglevel quiet -hide_banner -nostats",
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 0 -nostdin",
        }

    @property
    def song_queue(self):
        """This returns the song queue"""
        return self._song_queue[1:]

    @property
    def is_playing(self):
        """Shorthand for ``discord.VoiceClient.is_playing()``"""
        return self._voice_client.is_playing()

    async def queue(self, query, bettersearch=True):
        """Adds the query to the queue"""
        song = await get_video_data(self, query, bettersearch, self._loop)
        self._song_queue.append(song)
        self._bot.dispatch("disutils_music_queue", self._ctx, song)
        return song

    async def play(self):
        """This plays the first song in the queue"""
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(
            self._song_queue[0].source, **self._ffmpeg_options), self._volume)
        self._voice_client.play(
            source,
            after=lambda error: self._after_func(
                self._ctx,
                self._ffmpeg_options,
                self._music,
                self._after_func,
                self._loop,
            ),
        )
        song = self._song_queue[0]
        self._bot.dispatch("disutils_music_play", self._ctx, song)
        return song

    async def skip(self, force=True):
        """This skips the current song"""
        if not len(self._song_queue) > 1 and not force:
            raise EmptyQueue("Cannot skip because queue is empty")
        else:
            old = self._song_queue[0]
            old.is_looping = True if old.is_looping else False
            self._voice_client.stop()
            try:
                new = self._song_queue[1]
                self._bot.dispatch("disutils_music_skip", self._ctx, old, new)
                return (old, new)
            except IndexError:
                self._bot.dispatch("disutils_music_skip", self._ctx, old, None)
                return (old, None)

    async def stop(self):
        """Stops the player and clears the queue"""
        try:
            self._song_queue = []
            self._voice_client.stop()
            self._music._players.remove(self)
        except Exception as e:
            raise e
            raise NotPlaying("Cannot stop because nothing is being played")
        self._bot.dispatch("disutils_music_stop", self._ctx)

    async def pause(self):
        """Pauses the player"""
        try:
            self._voice_client.pause()
            song = self._song_queue[0]
        except:
            raise NotPlaying("Cannot pause because nothing is being played")
        self._bot.dispatch("disutils_music_pause", self._ctx, song)
        return song

    async def resume(self):
        """Resumes the player if it is paused"""
        try:
            self._voice_client.resume()
            song = self._song_queue[0]
        except:
            raise NotPlaying("Cannot resume because nothing is being played")
        self._bot.dispatch("disutils_music_resume", self._ctx, song)
        return song

    def now_playing(self):
        """Returns the song that is currently playing"""
        try:
            return self._song_queue[0]
        except:
            return None

    async def toggle_song_loop(self):
        """Toggles the current songs looping"""
        try:
            song = self._song_queue[0]
        except:
            raise NotPlaying("Cannot loop because nothing is being played")
        if not song.is_looping:
            song.is_looping = True
        else:
            song.is_looping = False
        self._bot.dispatch("disutils_music_toggle_loop", self._ctx, song)
        return song

    async def change_volume(self, vol: float):
        """Changes the volume of the player"""
        self._voice_client.source.volume = self._volume = vol
        try:
            song = self._song_queue[0]
        except:
            raise NotPlaying(
                "Cannot change volume because nothing is being played")
        self._bot.dispatch("disutils_music_volume_change",
                           self._ctx, song, vol)
        return (song, vol)

    async def remove_from_queue(self, index):
        """Removes a song from the queue"""
        if index == 0:
            try:
                song = self._song_queue[0]
            except:
                raise NotPlaying(
                    "Cannot remove from queue because nothing is being played")
            await self.skip(force=True)
            return song
        song = self._song_queue[index]
        self._song_queue.pop(index)
        self._bot.dispatch("disutils_music_queue_remove", self._ctx, song)
        return song

    def shuffle_queue(self):
        """Shuffles the queue"""
        # The reason i don't just use random.shuffle is because the 0. element is the current song and should not be shuffled
        self._song_queue = [self._song_queue[0], *
                            random.sample(self._song_queue[1:], len(self._song_queue[1:]))]
        self._bot.dispatch("disutils_music_queue_shuffle", self._ctx)
