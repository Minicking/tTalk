def test2(n):
    print('fuck',n)
    for i in range(n):
        yield i*i
        print("------%d*%d"%(i,i))
    yield 3838
x=[]
for i in test2(5):
    x.append(i)
    print("----%d-----"%(i))
print(x)
