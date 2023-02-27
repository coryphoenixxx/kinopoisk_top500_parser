from multiprocessing import Queue, Semaphore, Process, Manager

from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver


class Crawler:
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru/"
        self.movie_list_urls = [f"{self.base_url}/lists/movies/top500/?page={i + 1}" for i in range(10)]

    def run(self):
        return self.get_movie_urls()

    def get_movie_urls(self):
        with Manager() as manager:
            result = manager.list()
            sem = Semaphore(config.proc_nums)

            presets = Queue()
            for preset in config.presets:
                presets.put(preset)

            processes = []
            for link in self.movie_list_urls:
                proc = Process(target=self.get_movie_urls_job, args=(link, presets, sem, result))
                processes.append(proc)
                proc.start()

            for proc in processes:
                proc.join()

            print(len(result))

    @staticmethod
    def get_movie_urls_job(link, presets, sem, result):
        with sem:
            profile, window = presets.get()

            with WebDriver(link=link, profile=profile, window_rect=window) as driver:
                link_elems = driver.find_elements(By.CSS_SELECTOR, ".base-movie-main-info_link__YwtP1")
                result.extend([elem.get_attribute('href') for elem in link_elems])

            presets.put((profile, window))
