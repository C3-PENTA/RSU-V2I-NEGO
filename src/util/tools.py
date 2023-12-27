from time import sleep

class Counter:
    def __init__(self, max_num = None) -> None:
        if max_num is None:
            max_num = 255  # 0~127 1 byte
        self.max_num = max_num
        self.count = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if self.max_num < self.count:
            self.count = 0
        return self.count
    


if __name__ == '__main__':
    a = Counter(10)
    for i in range(400):
        print(f"{next(a)}")
        sleep(0.1)
    # print(next(a))
    # print(next(a))
    # print(next(a))
    # print(next(a))