import asyncio
import locale
import schedule
import time
import log

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
logger = log.setup_logger('scheduler', 'service.log')


async def realizar_verificacao():
    from telegram import enviar_mensagem_no_grupo
    from scraper import obter_dados
    dados = await obter_dados()
    if dados:
        mensagem = f'Nova mensagem de: {", ".join(dados)}'
        return await enviar_mensagem_no_grupo(mensagem)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    logger.info('Iniciando agendador...')
    schedule.every().hour.do(lambda: loop.run_until_complete(realizar_verificacao()))
    logger.info('Disparando tarefa imediatamente')
    schedule.run_all()
    logger.info(f'Tarefa agendada: {schedule.jobs}')
    while True:
        schedule.run_pending()
        time.sleep(1)
