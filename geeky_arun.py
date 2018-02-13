if __name__ == '__main__':
    q = int(raw_input())
    for i in range(q):
        j = int(raw_input())
        print(len(bin(j)[2:]))
