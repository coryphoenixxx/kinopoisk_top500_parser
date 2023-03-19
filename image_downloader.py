import asyncio
from asyncio import Semaphore
from collections import defaultdict

import aiofiles
import aiohttp
from tqdm import tqdm


class ImageDownloader:
    """Класс для асинхронной закачки изображений"""

    LIMIT = 32  # Количество одновременных соединений, дабы предотвратить DDOS

    def __init__(
            self,
            numbered_urls: list[tuple[int, str]],
            download_dir_creator: callable,
            filename: str,
            extension: str,
            pbar_desc: str,
            need_number: bool = False):
        """
        :param numbered_urls: Список пронумерованных ссылок на изображения
        :param download_dir_creator: Объект функции для создания папки, куда скачивать изображения
        :param need_number: Нужно ли дополнительное нумерование в имени файла
        """

        self._numbered_urls = numbered_urls
        self._download_dir_creator = download_dir_creator
        self._filename = filename
        self._extension = extension
        self._need_number = need_number
        self._pbar_desc = pbar_desc
        self._image_number_counter = defaultdict(int)
        self._download_counter = 0

    async def _async_download_image(
            self,
            sem: Semaphore,
            session: aiohttp.ClientSession,
            id_url_tuple: tuple[int, str]
    ):
        """Скачивание одного изображения"""

        image_id, image_url = id_url_tuple

        download_dir = self._download_dir_creator(image_id).mkdir()

        filename = self._filename
        if self._need_number:
            self._image_number_counter[image_id] += 1
            number = self._image_number_counter[image_id]
            filename = f"{filename}_{number}"

        filepath = download_dir / f"{filename}.{self._extension}"

        async with sem:
            for _ in range(20):
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        async with aiofiles.open(filepath, "wb") as f:
                            await f.write(content)
                        break
                    else:
                        await asyncio.sleep(1)
            else:
                print(f'{image_id} ({image_url}) — не скачано!')

        self._pbar.update(1)
        self._download_counter += 1
        if self._download_counter % 10:
            await asyncio.sleep(1)

    async def _async_download_images(self):
        coroutines = []
        sem = Semaphore(self.LIMIT)

        self._pbar = tqdm(total=len(self._numbered_urls), desc=self._pbar_desc)

        async with aiohttp.ClientSession() as session:
            for id_url_tuple in self._numbered_urls:
                coroutine = asyncio.create_task(
                    (self._async_download_image(sem, session, id_url_tuple))
                )
                coroutines.append(coroutine)
            await asyncio.gather(*coroutines)

    def run(self):
        asyncio.run(self._async_download_images())
