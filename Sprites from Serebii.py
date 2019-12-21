import requests
from time import sleep

AlolaNatNumbers = [103, 105]
GalarianNatNumbers = [110, 122, 222, 263, 264, 554, 555, 562, 618]

print('Beginning file download with requests')

Number = 1

for i in range(1, 722):
    
    if Number in range(1, 10):
        url = 'https://www.serebii.net/pokedex-swsh/icon/00' + str(i) + '.png'
    elif Number in range(10, 100):
        url = 'https://www.serebii.net/pokedex-swsh/icon/0' + str(i) + '.png'
    else:
        url = 'https://www.serebii.net/pokedex-swsh/icon/' + str(i) + '.png'
    
    r = requests.get(url)
    
    with open('/Users/Lucas/Downloads/Sprites/' + str(Number) + '.png', 'wb') as f:
        f.write(r.content)
    
    # Retrieve HTTP meta-data
    print(r.status_code)
    print(r.headers['content-type'])
    print(r.encoding)
    
    Number += 1
    
    if Number%50 == 0:
        sleep(5)

print('done')
