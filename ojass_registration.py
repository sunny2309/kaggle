import numpy as np

if __name__ == '__main__':
    N,Q = map(int,raw_input().split(' '))
    count_from_beg = []
    for i in range(N):
        i,out,count = map(int,raw_input().split(' '))
        if out > len(count_from_beg):
            count_from_beg.extend([0]*(out-len(count_from_beg)))
            count_from_beg[i-1:out] = [count+j for j in count_from_beg[i-1:out]]
        else:
            count_from_beg[i-1:out] = [count+j for j in count_from_beg[i-1:out]]
    for i in range(Q):
        s,t = map(int,raw_input().split(' '))
        #print(count_from_beg)
        print(max(count_from_beg[s-1:t]))        
    



