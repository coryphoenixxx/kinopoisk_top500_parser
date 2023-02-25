import time
from random import randint

from pathos.multiprocessing import ProcessPool
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import config
from custom_webriver import WebDriver
from utils import timeit


class Crawler:
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kinopoisk.ru/lists/movies/top500/?page={}"

    @timeit
    def run(self):
        links = [self.base_url.format(page_num + 1) for page_num in range(10)]

        with ProcessPool(ncpus=config.proc_nums) as pool:
            results = pool.map(self.job, zip(links, config.presets))

        return results

    @staticmethod
    def job(args):
        link, (profile, window) = args

        driver = WebDriver(profile=profile, window_rect=window)
        driver.show()

        time.sleep(randint(0, 2))

        driver.get(link)
        time.sleep(30)

        for _ in range(2):
            body = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        link_elems = driver.find_elements(By.CSS_SELECTOR, ".base-movie-main-info_link__YwtP1")

        result = [elem.get_attribute('href') for elem in link_elems]

        driver.quit()
        return result
