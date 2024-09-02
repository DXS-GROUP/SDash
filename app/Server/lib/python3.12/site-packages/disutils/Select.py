import asyncio
from typing import Union
import discord


class MultipleChoice:
    def __init__(self, ctx=None, question: Union[discord.Embed, str] = "Yes or no?", choices: Union[list, tuple] = ("👍", "👎"), timeout: float = 30.0):
        """This is the initializer for the MultipleChoice class.

        :param ctx: The context to run the class in. It doesn't have to be provided, but if it isn't, it must be provided to the run() method.
        :param question: The question to ask the user. This can be a string or an embed. If it's a string, it will be sent as a text message.
        :param choices: The choices to give the user. It must be a list or tuple of emojis. 
        :param timeout: The amount of time to wait for the user to respond. If the user doesn't respond in time, run() will return None."""
        self._ctx = ctx
        self.question = question
        self.timeout = timeout
        self.choices = choices

    async def run(self, ctx=None):
        if not self._ctx and not ctx:
            raise ValueError(
                "No context provided. please provide a context in either __init__() or run()")
        if not self._ctx:
            self._ctx = ctx

        if isinstance(self.question, discord.Embed):
            kwargs = {"embed": self.question}
        else:
            kwargs = {"content": self.question}

        message = await self._ctx.send(**kwargs)
        for choice in self.choices:
            await message.add_reaction(choice)

        def check(reaction, user):
            return user == self._ctx.author and str(reaction.emoji) in self.choices

        try:
            reaction, user = await self._ctx.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
            return self.choices.index(str(reaction.emoji))
        except asyncio.TimeoutError:
            return None


class Confirm(MultipleChoice):
    def __init__(self, ctx=None, question: Union[discord.Embed, str] = "Are you sure?", timeout: float = 30.0):
        super().__init__(ctx, question, choices=("✅", "❌"), timeout=timeout)

    async def run(self, ctx=None):
        ret = await super().run(ctx)
        return bool(ret) if type(ret) == int else None
