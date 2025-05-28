import html
import json
from json.decoder import JSONDecodeError
from urllib.parse import urlparse, urlunparse
from hoshino import Service


sv = Service('anti_zhihu', enable_on_default=True)


def unescape(param):
    param = param.replace('\\/', '/')
    return html.unescape(param)


def clean_url(url):
    parsed = urlparse(url)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        '',
        '',
        ''
    ))


def extract_json_data(msg):
    try:
        if msg.type == 'json':
            return json.loads(msg.data.get('data', ''))
        return None
    except JSONDecodeError:
        return None


def extract_zhihu_url(data):
    if data.get('app') == 'com.tencent.miniapp_01' and data.get('meta', {}).get('detail_1', {}).get('title') == '知乎':
        url = data.get('meta', {}).get('detail_1', {}).get('qqdocurl')
        if url:
            return clean_url(url)
    return None


@sv.on_message('group')
async def anti_zhihu(bot, event):
    msg = event.message[0]
    if not (data := extract_json_data(msg)):
        return
    if zhihu_url := extract_zhihu_url(data):
        sv.logger.info(f'[anti_zhihu INFO] 检测到知乎链接: {zhihu_url}')
        await bot.send(event, f'检测到知乎链接：\n{zhihu_url}')
        return