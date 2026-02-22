import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
from game_manager import MafiaGameManager
from views import GameMainMenu
import logging

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))

class MafiaBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_manager = MafiaGameManager(bot)
        self.cleanup_games.start()

    @app_commands.command(name="play", description="Начать новую игру в Мафию")
    @app_commands.describe(timeout="Время до начала игры в секундах (по умолчанию 60)")
    async def play(self, interaction: discord.Interaction, timeout: int = 60):
        """Создает новую игровую сессию"""
        try:
            # Проверяем, подключен ли пользователь к голосовому каналу
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.response.send_message(
                    "❌ Вы должны быть подключены к голосовому каналу!",
                    ephemeral=True
                )
                return

            guild = interaction.guild
            voice_channel = interaction.user.voice.channel

            # Проверяем, уже ли идет игра на этом сервере
            if self.game_manager.has_active_game(guild.id):
                await interaction.response.send_message(
                    "❌ На этом сервере уже идет игра! Дождитесь её окончания.",
                    ephemeral=True
                )
                return

            # Проверяем права бота
            if not voice_channel.permissions_for(guild.me).mute_members:
                await interaction.response.send_message(
                    "❌ Боту не хватает прав на отключение микрофонов!",
                    ephemeral=True
                )
                return

            # Создаем новую игру
            game = self.game_manager.create_game(
                guild_id=guild.id,
                guild=guild,
                voice_channel=voice_channel,
                text_channel=interaction.channel,
                initiator=interaction.user,
                timeout=timeout
            )

            # Подключаемся к голосовому каналу
            await voice_channel.connect()
            logger.info(f"Бот подключился к каналу {voice_channel.name} на сервере {guild.name}")

            # Отправляем главное меню с кнопками
            menu = GameMainMenu(game, self.game_manager)
            embed = self._create_game_embed(game)
            
            await interaction.response.send_message(
                embed=embed,
                view=menu
            )

            game.message = await interaction.original_response()
            logger.info(f"Игра {game.game_id} создана на сервере {guild.id}")

        except Exception as e:
            logger.error(f"Ошибка в команде /play: {e}", exc_info=True)
            try:
                await interaction.response.send_message(
                    f"❌ Произошла ошибка: {str(e)}",
                    ephemeral=True
                )
            except:
                pass

    def _create_game_embed(self, game):
        """Создает embed для отображения статуса игры"""
        embed = discord.Embed(
            title="🎭 Игра в Мафию",
            description="Добро пожаловать в игру!",
            color=discord.Color.purple()
        )
        
        players_text = "\n".join([f"• {p.user.mention}" for p in game.players]) if game.players else "Ещё никто не присоединился"
        
        embed.add_field(
            name=f"👥 Участники ({len(game.players)}/15)",
            value=players_text,
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Статус",
            value="⏳ Ожидание игроков...",
            inline=False
        )
        
        embed.set_footer(text=f"Игра ID: {game.game_id}")
        return embed

    @tasks.loop(minutes=5)
    async def cleanup_games(self):
        """Периодически очищает завершенные игры"""
        try:
            self.game_manager.cleanup_finished_games()
            logger.info("Проведена очистка завершенных игр")
        except Exception as e:
            logger.error(f"Ошибка при очистке игр: {e}")

    @cleanup_games.before_loop
    async def before_cleanup(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(MafiaBot(bot))


def create_bot():
    """Создает и настраивает бота"""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    intents.members = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Бот {bot.user} готов к работе!")
        try:
            synced = await bot.tree.sync()
            logger.info(f"Синхронизировано {len(synced)} команд")
        except Exception as e:
            logger.error(f"Ошибка синхронизации команд: {e}")

    return bot


if __name__ == "__main__":
    bot = create_bot()
    
    @bot.setup_hook
    async def load_cogs():
        await setup(bot)
    
    bot.run(TOKEN)