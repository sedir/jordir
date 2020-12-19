import asyncio

from config import settings
from aiogram import Bot, Dispatcher, types
import log
import scraper

logger = log.setup_logger('telegram', 'service.log')
bot = Bot(token=settings.TOKEN)
dp = Dispatcher(bot=bot)


@dp.message_handler(commands=['log'])
async def ver_log(message: types.Message):
    with open("service.log", "r") as log_file:
        lines = log_file.readlines()[-10:]
        await message.reply(''.join(lines))


async def enviar_mensagem_no_grupo(mensagem):
    await bot.send_message(settings.ID_GRUPO, mensagem)


@dp.message_handler(commands=['verificar'])
async def verificar(message: types.Message):
    msg = await bot.send_message(message.chat.id, 'Verificando... ⌛︎')
    try:
        dados = await scraper.obter_dados()

        if not dados:
            await msg.edit_text('Nada novo sob o sol 🤷')
        else:
            await msg.edit_text('Opa! 🚨 Tem mensagem de: '+', '.join(dados))
    except:
        await msg.edit_text('Deu treta, veja os logs e tente de novo 🚫')


async def main():
    try:
        logger.info('Iniciando bot.')
        await dp.start_polling()
    finally:
        logger.info('Encerrando bot.')
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
