import time

from pathos.multiprocessing import ProcessPool
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import config
from custom_webriver import WebDriver
from utils import timeit


class Crawler:
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru/"
        self.movie_list_urls = [f"{self.base_url}/lists/movies/top500/?page={i + 1}" for i in range(10)]

    def run(self):
        self.catch_captcha()
        results = self.get_movie_urls()
        return results

    def catch_captcha(self):
        with ProcessPool(ncpus=config.proc_nums) as pool:
            pool.map(self.catch_captcha_job, zip([self.base_url] * config.proc_nums, config.presets))

    @timeit
    def get_movie_urls(self):
        with ProcessPool(ncpus=config.proc_nums) as pool:
            return pool.map(self.get_movie_urls_job, zip(self.movie_list_urls, config.presets))

    @staticmethod
    def catch_captcha_job(args):
        link, (profile, window) = args

        driver = WebDriver(profile=profile, window_rect=window).get(link)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

        try:
            driver.find_element(By.CSS_SELECTOR, ".CheckboxCaptcha-Button").click()
        except NoSuchElementException:
            pass

        while 'showcaptcha' in driver.current_url:
            time.sleep(1)

        driver.quit()

    @staticmethod
    def get_movie_urls_job(args):
        link, (profile, window) = args

        driver = WebDriver(profile=profile, window_rect=window).get(link)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

        link_elems = driver.find_elements(By.CSS_SELECTOR, ".base-movie-main-info_link__YwtP1")

        result = [elem.get_attribute('href') for elem in link_elems]

        driver.quit()
        return result
