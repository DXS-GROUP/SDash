from typing import List, Literal
import discord
import asyncio


class v1_x_Paginator:
    def __init__(self, ctx, pages: List[discord.Embed], auto_footer: bool = False, commands: dict = {"⏮️": "first", "⏪": "previous", "⏹": "stop", "⏩": "next", "⏭️": "last"}, timeout: float = 60.0, on_stop: Literal["remove_reactions", "delete_message", None] = None, start_page: int = 0):
        self.ctx = ctx
        self.bot = ctx.bot
        self.pages = pages
        self.auto_footer = auto_footer
        self.commands = commands
        self.timeout = timeout
        self.on_stop = on_stop
        self.current_page = start_page

    async def run(self):
        if self.auto_footer:
            for page in self.pages:
                page.set_footer(
                    text=f"Page {self.pages.index(page) + 1} of {len(self.pages)}")

        self.message = await self.ctx.send(embed=self.pages[self.current_page])

        for command in self.commands:
            await self.message.add_reaction(command)

        def check(reaction, user):
            return user == self.ctx.author and reaction.message.id == self.message.id and str(reaction.emoji) in self.commands.keys()

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=self.timeout, check=check)
                command = self.commands[str(reaction.emoji)]

                if command == "stop":
                    return await self.stop()

                elif command == "first":
                    self.current_page = 0

                elif command == "previous":
                    if self.current_page > 0:
                        self.current_page -= 1

                elif command == "next":
                    if self.current_page < len(self.pages) - 1:
                        self.current_page += 1

                elif command == "last":
                    self.current_page = len(self.pages) - 1

                elif command.startswith("page"):
                    try:
                        page = int(command.split("page")[1])
                        if page > 0 and page <= len(self.pages):
                            self.current_page = page - 1
                    except:
                        raise ValueError("Invalid page number")

                await self.message.remove_reaction(str(reaction.emoji), user)
                await self.message.edit(embed=self.pages[self.current_page])

            except asyncio.TimeoutError:
                return await self.stop()

    async def stop(self):
        if self.on_stop == "remove_reactions":
            await self.message.clear_reactions()
        elif self.on_stop == "delete_message":
            await self.message.delete()


class v2_x_Paginator(v1_x_Paginator):
    def __init__(self, ctx, pages: List[discord.Embed], auto_footer: bool = False, commands: dict = {"⏮️": "first", "⏪": "previous", "⏹": "stop", "⏩": "next", "⏭️": "last"}, timeout: float = 60.0, on_stop: Literal["remove_buttons", "disable_buttons", "delete_message", None] = None, start_page: int = 0, button_style: discord.ButtonStyle = discord.ButtonStyle.primary, stop_button_style: discord.ButtonStyle = discord.ButtonStyle.danger):
        self.button_style = button_style
        self.stop_button_style = stop_button_style

        self.view = discord.ui.View(timeout=timeout)
        for button in self._generate_buttons(commands):
            self.view.add_item(button)
        self.view.on_timeout = self.stop

        super().__init__(ctx, pages, auto_footer, commands, timeout, on_stop, start_page)

    def _generate_buttons(self, commands: dict):
        self.buttons = []
        for emoji, command in zip(commands.keys(), commands.values()):
            button = discord.ui.Button(
                emoji=emoji, style=self.stop_button_style if command == "stop" else self.button_style)
            button.callback = self._get_callback(command)
            self.buttons.append(button)
        return self.buttons

    def _get_callback(self, command):
        async def _callback(interaction):
            await self._handle_command(command, interaction)
        return _callback

    async def run(self):
        if self.auto_footer:
            for page in self.pages:
                page.set_footer(
                    text=f"Page {self.pages.index(page) + 1} of {len(self.pages)}")

        self.message = await self.ctx.send(embed=self.pages[self.current_page], view=self.view)

    async def _handle_command(self, command, interaction):
        if command == "stop":
            await interaction.response.defer()
            return await self.stop()

        elif command == "first":
            self.current_page = 0

        elif command == "previous":
            if self.current_page > 0:
                self.current_page -= 1

        elif command == "next":
            if self.current_page < len(self.pages) - 1:
                self.current_page += 1

        elif command == "last":
            self.current_page = len(self.pages) - 1

        elif command.startswith("page"):
            try:
                page = int(command.split("page")[1])
                if page > 0 and page <= len(self.pages):
                    self.current_page = page - 1
            except:
                raise ValueError("Invalid page number")

        await interaction.response.edit_message(embed=self.pages[self.current_page])

    async def stop(self):
        if self.on_stop == "remove_buttons":
            await self.message.edit(view=None)
        elif self.on_stop == "disable_buttons":
            for button in self.buttons:
                button.disabled = True
            await self.message.edit(view=discord.ui.View(*self.buttons))
        elif self.on_stop == "delete_message":
            await self.message.delete()

        if not self.view.is_finished():
            self.view.stop()


if discord.version_info.major == 1:
    Paginator = v1_x_Paginator
elif discord.version_info.major == 2:
    Paginator = v2_x_Paginator
