import bs4 as bs
from urllib.request import Request, urlopen
import re
import sys
from databaseAdder import addToBD
from brandlist import brandlist
p=1
f = open('SB3.txt', 'w')

shopID=1

page = 'https://street-beat.ru/cat/krossovki;kedy/?page='

req = Request((page + str(p)), headers={'User-Agent': 'Mozilla/5.0'})
sauce = urlopen(req).read()
soup = bs.BeautifulSoup (sauce, 'lxml')
lastpage=((soup.find(class_="catalog-pagination__pages")).select_one("a:nth-of-type(2)")).text

print(lastpage)
while p < int(lastpage):
    print(p)
    req = Request((page + str(p)), headers={'User-Agent': 'Mozilla/5.0'})
    sauce = urlopen(req).read()
    soup = bs.BeautifulSoup (sauce, 'lxml')    
    for sneaker in soup.find_all("a", class_="catalog-item__img-wrapper"):        
        url = 'https://street-beat.ru'+ str(sneaker.get('href'))
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        sauce = urlopen(req).read()
        soup = bs.BeautifulSoup (sauce, 'lxml')
        try:         
            price=(soup.find(class_="price--current")).text
            lastPrice=(soup.find(class_="price--old")).text
            lastPrice=re.sub(r'[^0-9]','', lastPrice)
            if lastPrice:
                sale=True
            else:
                lastPrice=None
                sale=False
            #brand=soup.select_one(".product-heading span:nth-of-type(1)").text
            model=soup.select_one(".product-heading span").text
            vendorcode=(soup.find(class_="product-article")).text
            img = 'https://street-beat.ru' + soup.find(attrs={'data-fancybox':'gallery'}).get('href')
            sizes=[]
            for size in (soup.find(attrs={'data-size-type': 'eu'})).findAll(class_="radio__label"): 
                sizes.append(size.get('data-size'))
        except:
            print("не вышло спарсить" + url) 
        try:
            if re.match(r'Мужские', model) is not None:
                sex='M'
            elif re.match(r'Женские', model) is not None:
                sex='W'
            else:
                sex='MW'
            model = re.sub(r'[а-яА-Я]', '', model).lstrip()
            brand=None
            for n in brandlist:
                m=re.match(n, model.lower())
                if m is not None:
                    brand=n
                    model=model[m.end():].lstrip()
                    break
            if brand is None:
                continue
            vendorcode=re.sub(r'[а-яА-Я\s\.]', '', vendorcode)
            price=re.sub(r'[\D]', '', price)
        except:
            print("не вышло нормализировать" + url) 
        try:
            f.write("\n")
            f.write(brand)
            f.write("\n")
            f.write(sex)
            f.write("\n")
            f.write(model)
            f.write("\n")
            f.write(price)
            f.write("\n")
            f.write(vendorcode)
            f.write("\n")
            f.write(url)
            f.write("\n")
            f.write(img)
            f.write("\n")
            f.write(str(sizes))
            f.write("\n")
            for element in sizes:
                element=re.sub(',', '.', element) 

            addToBD(str(vendorcode), brand, str(model), sex, str(price), url, img, str(sizes), str(shopID), str(sale), lastPrice)
            f.write('Записан')
            f.write("\n")
        except:
            print("не вышло записать в базу " + vendorcode +  ' '  +  brand +  ' '  +  str(model) + str(lastPrice))              
    p=p+1
f.close() 