import bs4 as bs
import urllib.request
import re
from databaseAdder import addToBD
from brandlist import brandlist
page = 'https://kixbox.ru/catalog/new/?SHOWALL_1=1&FILTER=19173'

shopID=2
i = 1
f = open('KIXBOX.txt', 'w')
for i in range(2):
    source = urllib.request.urlopen(page).read()
    soup = bs.BeautifulSoup (source, 'lxml')
    soup = soup.find("div", class_="catalog-grid")

    for each_div in soup.find_all("div", class_="product"):
        soup = each_div
        link = soup.a
        prettylink = 'https://kixbox.ru' + link.get('href')

        sauce = urllib.request.urlopen(prettylink).read()
        soup = bs.BeautifulSoup (sauce, 'lxml')       
        brand = soup.find(class_="product-info__title").text

        if brand.lower() not in brandlist:
            continue
        model = soup.find(class_="product-brand__text").text
        vendorcode = soup.find(class_="product-info__article").text
        
        price = soup.find(class_="product-info__price")
        if 'price__old' in str(price):
            sale=True
            lastPrice=price.select_one("span").text
            price=price.text.replace(lastPrice, '')
            lastPrice=re.sub(r'[а-яА-Я\s\.:\W]', '', lastPrice)
        else:
            price=price.text
            lastPrice=None
            sale=False

        sizes=[]        
        for size in ((soup.find(class_="chosen-select")).findAll('option')):
            if 'disabled' not in str(size):            
                sizes.append(re.sub('EU','', size.text))

        img='https://kixbox.ru/' + (soup.select_one("div .slider-product-big__slide")).find('img').get('src')

        if re.match(r'Мужские', model) is not None:
            sex='M'
        elif re.match(r'Женские', model) is not None:
            sex='W'
        else:
            sex='MW'
        model = re.sub(r'[а-яА-Я]', '', model).lstrip()

        vendorcode=re.sub(r'[а-яА-Я\s\.:]', '', vendorcode)
        price=re.sub(r'[а-яА-Я\s\.:\W]', '', price)

        addToBD(str(vendorcode), brand, str(model), sex, str(price), prettylink, img, str(sizes), str(shopID), str(sale), lastPrice)
    page = 'https://kixbox.ru/catalog/sale/?SHOWALL_1=1&FILTER=19173'