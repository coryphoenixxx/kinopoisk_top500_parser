import asyncio
from asyncio import Semaphore
from collections import defaultdict

import aiofiles
import aiohttp
from tqdm import tqdm


class ImageDownloader:
    LIMIT = 64

    def __init__(self):
        self._numbered_urls = None
        self._download_dir_creator = None
        self._prefix = None
        self._extension = None
        self._need_number = None
        self._pbar = None
        self._image_number_counter = defaultdict(int)
        self._get_counter = 0

    async def _async_download_image(self, sem, session, id_url_tuple):
        image_id, image_url = id_url_tuple

        download_dir = self._download_dir_creator(image_id).obj

        prefix = self._prefix
        if self._need_number:
            self._image_number_counter[image_id] += 1
            number = self._image_number_counter[image_id]
            prefix = f"{prefix}_{number}"

        filepath = download_dir / f"{prefix}.{self._extension}"

        async with sem:
            for _ in range(10):
                async with session.get(image_url) as response:
                    if response.status == 200:
                        content = await response.read()
                        async with aiofiles.open(filepath, "wb") as f:
                            await f.write(content)
                        break
                    else:
                        await asyncio.sleep(0.5)
                        continue

        self._pbar.update(1)
        self._get_counter += 1
        if self._get_counter % 10:
            await asyncio.sleep(0.5)

    async def _async_download_images(self):
        coroutines = []
        sem = Semaphore(self.LIMIT)

        async with aiohttp.ClientSession() as session:
            for id_url_tuple in self._numbered_urls:
                coroutine = asyncio.create_task(
                    (self._async_download_image(sem, session, id_url_tuple))
                )
                coroutines.append(coroutine)
            await asyncio.gather(*coroutines)

        self._pbar = None

    def run(self, numbered_urls, download_dir_creator, prefix, extension, pbar_desc, need_number=False):
        self._numbered_urls = numbered_urls
        self._download_dir_creator = download_dir_creator
        self._prefix = prefix
        self._extension = extension
        self._need_number = need_number
        self._pbar = tqdm(total=len(numbered_urls), desc=pbar_desc)

        asyncio.run(self._async_download_images())
