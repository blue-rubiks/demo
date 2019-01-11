from collections import Counter

urls = [
    "http://www.google.com/a.txt",
    "http://www.google.com.tw/a.txt",
    "http://www.google.com.tw/download/c.jpg",
    "http://www.google.co.jp/a.txt",
    "http://www.google.com/b.txt",
    "http://www.facebook.com/movie/b.txt",
    "http://yahoo.com/123/000/c.jpg",
    "http://gliacloud.com/haha.png",
]

if __name__ == "__main__":

    count_dict = dict()
    for url in urls:
        file_name = url.split("/")[-1]
        if file_name in count_dict:
            count_dict[file_name] += 1
        else:
            count_dict[file_name] = 1
    c = Counter(count_dict)
    count_dict = sorted(c.most_common(3), key=lambda x: (x[0], x[1]))
    for key, val in count_dict:
        print('{} {}'.format(key, val))

# a.txt 3
# b.txt 2
# c.jpg 2
