import re
from bs4 import BeautifulSoup
from PIL import Image
import aiohttp
import tempfile
import discord
import os

tmp = tempfile.gettempdir()

async def get_gif_url_tenor(view_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(view_url) as response:
            page_content = await response.text()

    soup = BeautifulSoup(page_content, 'html.parser')
    meta_tags = soup.find_all('meta', {'class': 'dynamic'})

    urls = []


    for tag in meta_tags:
        content = tag.get('content', '')
        url_matches = re.findall(r'https?://[^\s]+', content)
        urls.extend(url_matches)

    second_url = urls[1] if len(urls) >= 3 else None
    return second_url

async def download_attachment(message, queue):
    queue.put('[DEBUG] Function download_attachment called')
    global tmp
    if isinstance(message, discord.Message):
        url = message.reference.resolved.attachments[0].url if message.reference.resolved.attachments else message.reference.resolved.content
    elif isinstance(message, str):
        url = message
        
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                if '.gif' in url: extension = '.gif'
                elif '.png' in url: extension = '.png'
                elif url in ['.jpg', '.jpeg']: extension = '.jpg'
                elif '.webp' in url: extension = '.webp'
                else:
                    queue.put(f'[DEBUG] Function download_attachment: Invalid extension {extension}')
                    return f'Invalid extension {extension}'

                path = os.path.join(tmp, f'original_image{extension}')
                queue.put(f'[DEBUG] Function download_attachment: Detected extension {extension}.')
                queue.put(f'[DEBUG] Function download_attachment: Starting download...')
                with open(path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
            else:
                queue.put(f'[DEBUG] Function download_attachment failed.{response.status} - {response.reason}')
                raise BaseException(f"Failed to caption the image: {response.status} - {response.reason}")

    queue.put(f'[DEBUG] Function download_attachment: Finished succesfully. {path}')
    return path

def is_animated(path):
    try:
        img = Image.open(path)
        img.seek(1)
        return True
    except EOFError:
        return False