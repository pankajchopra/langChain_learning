import time


def time_taken(func):
    def wrapper(*args, **kwargs):
        start_time = time.time_ns()
        print(start_time)
        result = func(*args, **kwargs)
        end_time = time.time_ns()
        print(end_time)
        elapsed_time = end_time - start_time

        print(f"Time taken: {elapsed_time:.9f}  nano seconds")
        return result

    return wrapper
