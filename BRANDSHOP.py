import re
import bs4 as bs
import urllib.request
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from databaseAdder import addToBD
from brandlist import brandlist

chrome_options = Options()
chrome_options.add_argument("--headless --blink-settings=imagesEnabled=false --disable-gpu --disable-extensions")
chrome_driver = os.getcwd() +"\\chromedriver.exe"
driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

page = 'https://brandshop.ru/sneakers/?page='
shopID=3
p = 1
amount = 0
#OOFrow is № of out of stock sneakers in a row
OOFrow=0
f = open('BRANDSHOP.txt', 'w')
while OOFrow < 7:
    sauce = urllib.request.urlopen((page + str(p))).read()
    soup = bs.BeautifulSoup (sauce, 'lxml')

    for sneaker in soup.find_all("div", class_="product-container"):
        if sneaker.find(class_='product outofstock') is not None:
            OOFrow +=1
            continue
        OOFrow=0
        url = sneaker.find('a', class_='product-image').get('href')
        if url == "javascript:void(0);":
            continue
        sauce = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup (sauce, 'lxml')  

        brand = soup.find(attrs={'itemprop': 'brand'}).text.rstrip()     
        if brand.lower() not in brandlist:
            continue            
        model = soup.find(attrs={'itemprop': 'name'}).text

        img=soup.find(attrs={'itemprop': 'image'}).get('src')

        if soup.find(class_='price price-box').get('data-sale') == 'sale:true':
            sale=True
            lastPrice=soup.find(class_='regprice').text
            lastPrice=re.sub(r'[\D]', '', lastPrice)
        else:
            lastPrice=0
            sale=False

        price = soup.find(attrs={'itemprop': 'price'}).text
        vendorcode = (soup.find("div", class_="description")).div.text

        if re.match(r'Мужские', model) is not None:
            sex='M'
        elif re.match(r'Женские', model) is not None:
            sex='W'
        else:
            sex='MW'
        model = re.sub(r'[а-яА-Я]', '', model).lstrip()
        price=re.sub(r'[\D]', '', price)
        vendorcode=re.sub(r'[а-яА-Я\s\.]', '', vendorcode)
        
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
        f.write(str(sale))
        f.write("\n")
        driver.get(url)
        
        try:
            element = driver.find_element_by_class_name('options')
            bla = element.get_attribute('innerHTML')            
            soup = bs.BeautifulSoup (bla, 'lxml')

            sizes = []
            for size in soup.find_all("div"):
                value=size.find(class_="text").text
                value=re.sub('[.]', ',', value)
                sizes.append(re.sub(r'[^\d^,]', '', value))
            amount += 1
        except:
            {}
        f.write(str(sizes))
        addToBD(str(vendorcode), brand, str(model), sex, str(price), url, img, str(sizes), str(shopID), str(sale), lastPrice)
    
    p += 1
    
    print(page)
driver.quit()
print("Всего:", amount)