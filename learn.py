dic = {
    'cc': {'time': '123133', 'nickname': ''},
    'aa': {'time': '123123', 'nickname': ''},
    'bb': {'time': '123124', 'nickname': ''}
}
print(sorted(dic.items(), key=lambda value: value[1]['time']))
for i in dic.values():
    print(i)
