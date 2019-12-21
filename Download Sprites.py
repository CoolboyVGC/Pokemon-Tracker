import requests
from time import sleep
import os

print('Beginning to download sprites from serebii')

Number = 1

for i in range(1, 891):
    
    if Number in range(1, 10):
        url = 'https://www.serebii.net/pokedex-swsh/icon/00' + str(i) + '.png'
    elif Number in range(10, 100):
        url = 'https://www.serebii.net/pokedex-swsh/icon/0' + str(i) + '.png'
    else:
        url = 'https://www.serebii.net/pokedex-swsh/icon/' + str(i) + '.png'
    
    r = requests.get(url)
    
    with open(os.path.join('Pokemon Sprites', str(Number)+'.png'), 'wb') as f:
        f.write(r.content)
    
    print('Succesfully downloaded the sprite of ' + str(Number))
    
    Number += 1
    
    if Number%50 == 0:
        sleep(5) #Serebii blocks requests after 50, so a 5s timeout is needed

print('done')
