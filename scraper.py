import pandas as pd
from pyppeteer import launch
import os
import json
import dictdiffer
from addict import Dict
import locale
import logging
import log
from config import settings

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
logger = log.setup_logger('scraper', 'service.log')


def tratar_dataframe(df):
    del df['Autor']
    del df['Tópico']
    del df['Unnamed: 6']
    df.rename(columns={'Autor.1': 'Aluno'}, inplace=True)
    df['Data última mensagem'] = pd.to_datetime(df['Última mensagem'].map(lambda t: t[len(t) - 23:]),
                                                format="%a, %d %b %Y, %H:%M").dt.strftime('%Y-%m-%d %H:%M')
    df['Autor última mensagem'] = df['Última mensagem'].map(lambda t: t[:len(t) - 23])
    del df['Última mensagem']
    df.set_index('Aluno', inplace=True)
    return df


def processar_dados(dados):
    filename = 'ultimos_dados.json'
    file_exists = os.path.exists(filename)
    if not file_exists:
        logger.info(f'Primeira vez rodando, então criando dados de parâmetro...')
        with open(filename, 'w') as f:
            json.dump(dados, f)
    else:
        with open(filename, 'r') as f:
            dados_antigos = json.load(f)
            diffs = list(dictdiffer.diff(dados_antigos, dados))
            dict_diff = Dict()
            for status, key, (old, new) in diffs:
                if status == 'change':
                    path = ''
                    for x in key.split('.'):
                        path += f'["{x}"]'
                    exec(f'dict_diff{path} = "{new}"')
            alunos = []
            for key, value in dict_diff.items():
                if 'Autor última mensagem' in value.keys():
                    if any([x in value['Autor última mensagem'] for x in ['JORDANA', 'SEDIR']]):
                        continue
                alunos.append(key)
            if alunos:
                logger.info(f'Existe pelo menos uma mensagem de: {", ".join(alunos)}')
            else:
                logger.info(f'Nada novo sob o sol.')
        with open(filename, 'w') as f:
            json.dump(dados, f)
        return alunos


async def obter_dados():
    browser = await launch(executablePath='/usr/bin/google-chrome-stable', args=['--no-sandbox'])
    page = await browser.newPage()
    logger.info('Acessando Sabiá...')
    await page.goto('https://login.sabia.ufrn.br/entrar/')
    await page.waitFor(2000)
    await page.type('#id_username', settings.SABIA_USUARIO)
    await page.type('#id_password', settings.SABIA_SENHA)
    logger.info('Autenticando...')
    await page.keyboard.press('Enter')
    await page.waitFor(2000)
    logger.info('Acessando AVASUS...')
    await page.goto('https://avasus.ufrn.br/login/index.php')
    await page.waitFor(2000)
    dados = {}
    for i in range(2):
        logging.info(f'Acessando fórum, página {i}...')
        await page.goto(f'https://avasus.ufrn.br/mod/forum/view.php?f=8298&page={i}')
        await page.waitFor(2000)
        df = tratar_dataframe(pd.read_html(await page.content())[2])
        dados |= df.to_dict('index')

    logger.info(f'Dados obtidos. Saindo do Sabiá...')
    await page.goto('https://login.sabia.ufrn.br/sair/')
    await page.waitFor(2000)
    await browser.close()

    logger.info(f'Iniciando análise de diferenças...')
    dados_processados = processar_dados(dados)
    return dados_processados
