from crawler import Crawler
from utils import timeit


@timeit
def main():
    crawler = Crawler()
    print(crawler.run())


if __name__ == '__main__':
    main()
