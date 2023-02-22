from pages_downloader import Crawler
from multiprocessing import Pool

import screeninfo


if __name__ == '__main__':
    monitor = screeninfo.get_monitors()[0]
    w, h = int(monitor.width), int(monitor.height) - 20

    window_params = [
        (w, h, 0, 0),
        (w, h, w // 2, 0),
        (w, h, 0, h // 2),
        (w, h, w // 2, h // 2)
    ]

    crawler = Crawler()

    with Pool(processes=4) as p:
        p.map(crawler.start, window_params)
