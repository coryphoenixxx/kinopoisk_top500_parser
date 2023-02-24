import os

from pages_downloader import Crawler
from multiprocessing import Pool
import screeninfo
from collections import deque, namedtuple
from dotenv import load_dotenv

from pathos.multiprocessing import ProcessingPool as Pool

if __name__ == '__main__':
    load_dotenv()

    monitor = screeninfo.get_monitors()[0]
    window_width, window_height = int(monitor.width) // 2, (int(monitor.height) - 20) // 2

    profile_dirs = os.getenv('CHROME_PROFILE_DIRS').split(',')
    parent_dirs = os.getenv('CHROME_PROFILE_PARENT_DIRS').split(',')
    delays = [0, 2, 4, 6]
    window_rects = [
        (0, 0, window_width, window_height),
        (window_width, 0, window_width, window_height),
        (0, window_height, window_width, window_height),
        (window_width, window_height, window_width, window_height)
    ]

    presets = deque(zip(window_rects, parent_dirs, profile_dirs, delays))

    # CONFIG = namedtuple('CONFIG', 'window_rect, parent_dir, profile_dir, delay, link')

    params = []

    for i in range(10):
        p = presets[0]
        config = dict(
            window_rect=p[0],
            parent_dir=p[1],
            profile_dir=p[2],
            delay=p[3],
            link=f'https://www.kinopoisk.ru/lists/movies/top500/?page={i + 1}'
        )
        params.append(config)
        presets.rotate(-1)


    crawler = Crawler()

    pool = Pool(ncpus=4)
    results = pool.map(crawler.start, params)

    final = [item for sublist in results for item in sublist]

    print(len(final))
