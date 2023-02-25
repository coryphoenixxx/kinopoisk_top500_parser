from crawler import Crawler

if __name__ == '__main__':
    crawler = Crawler()
    results = crawler.run()

    final = [item for sublist in results for item in sublist]
    print(len(final))

