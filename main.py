import os

from crawler import Crawler
from dotenv import load_dotenv
from custom_webriver import WebDriver

if __name__ == '__main__':
    load_dotenv()

    WebDriver.generate_settings(int(os.getenv('PROCESS_NUM')))

    crawler = Crawler()
    results = crawler.run()

    final = [item for sublist in results for item in sublist]
    print(len(final))
