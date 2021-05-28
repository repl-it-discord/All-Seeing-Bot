import os
import sys
import discord
import asyncio
import webserver
from discord.ext import commands
from discord.ext.commands import AutoShardedBot as asb
from background_tasks import bg_tasks, spam_chart_daemon
from utils import check_command, is_dev
import importlib

async def prefix(bot, message):
    return "?" if message.guild.id == 437048931827056642 else "$"

started = False

class AllSeeingBot(asb):
    def __init__(self):
        super().__init__(
            command_prefix=self.prefix,
            case_insensitive=True,
            intents=discord.Intents.all(), # remove this if you dont have all intents enabled
            help_command=None
        )
        
        self.cog_folders = [
            "Commands",
            "Moderation",
            "Other"
        ]
        self.cog_blacklist = [
            "__init__.py"
        ]
        
        if not started:
            print("Loading cogs:")
            for file in os.listdir("."):
                if os.path.isdir(f"./{file}") and file in self.cog_folders:
                    for script in os.listdir(f"./{file}"):
                        if script.endswith(".py") and not script in self.cog_blacklist:
                            try:
                                self.load_extension(f"{file}.{script[:-3]}")
                                print(f"    Loaded '{script}'")
                            except Exception as e:
                                print(str(e))
                        elif not "." in script and os.path.isdir(f"./{file}/{script}"):
                            print(f"    Loading cogs from '{script}':")
                            for script1 in os.listdir(f"./{file}/{script}"):
                                try:
                                    self.load_extension(f"{file}.{script}.{script1}")
                                    print(f"    Loaded '{script1}'")
                                except Exception as e:
                                    print(str(e))
            started = True
                        
    def testFunc(self, ctx: commands.Context) -> bool:
        return ctx.guild.id == 437048931827056642

    @commands.command(name="helper")
    @commands.check(testFunc)
    async def toggle_helper_role(self, ctx: commands.Context, name: str):
        try:
            role = await converter.convert(ctx, f'help-{name}')
        except commands.errors.BadArgument:
            await ctx.send("nope nope doesnt exist nice try")
            return
        
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
        else:
            await ctx.author.add_roles(role)
        
        await ctx.send('done')

    async def on_ready():
        bot.add_check(check_command)
        await bot.change_presence(
            activity=discord.Activity(
                name='everything', type=discord.ActivityType(3)
            )
        )
        # print(len(bot.commands))
        if not started():
            bot.loop.create_task(spam_chart_daemon(bot))
            bot.loop.create_task(bg_tasks(bot))

        # print('ready')

    async def on_command_error(ctx, error):
        if type(error) == commands.errors.CheckFailure:
            await ctx.message.delete()
            msg = await ctx.send(f"You cant use `{ctx.prefix}{ctx.command}` here...")
            await asyncio.sleep(3)
            await msg.delete()
        else:
            raise error

if __name__ == "__main__":
    webserver.keep_alive(bot)
    token = os.environ.get("DISCORD_BOT_SECRET")
    bot = AllSeeingBot()
    bot.run(token)
