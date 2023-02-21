from functools import wraps
import time


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


class Navigator:
    @staticmethod
    def get_one_movie_path(num: int) -> str:
        """Функция отвечает за выдачу ссылки на один фильм"""
        return f'./pages_movies/movie_{num}.html'

    @staticmethod
    def get_movies_page_path(num: int) -> str:
        """Функция отвечает за нумерацию общих страниц с фильмами"""
        return f'./pages_list_movies/movies_page_{num}.html'
