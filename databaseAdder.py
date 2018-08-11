import psycopg2
import urllib.request
import datetime
import os

def addToBD(vendorcode, brand, model, sex, price, url, img, sizes, shopID, sale, lastPrice):       
    try:
        conn = psycopg2.connect("dbname='SneakerDB1' user='postgres' host='localhost' port='5000' password='1'")
    except:
        print ("unable to connect to the database")
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sneakers where vendorcode='{vendorcode}'")
        records = cursor.fetchone()
        date=datetime.date.today()
        brand=brand.upper()
        vendorcode=vendorcode.replace('/', '')
    except:
        print ("Какая то хуета с курсором")
    if records is None:
        print("ДОБАВЛЯЕМ В SNEAKERS " + vendorcode) 
        #скачиваем картинку
        try:
            imgFilename=vendorcode+ '_' + str(date) +'.jpg'
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            imagepath=os.getcwd() + f'/images/{imgFilename}'
            urllib.request.urlretrieve(img, imagepath)
        except:
            print(f'не удалось скачать картинку {imgFilename} {img}')
        #записываем в базу        
        try:
            model=model.replace("\'","\'\'")
            cursor.execute(f"INSERT INTO sneakers (vendorcode, brand, model, sex, image) values ('{vendorcode}', '{brand}', '{model}', '{sex}', '{imgFilename}');")            
        except:
            print(f"не удалось записать в Sneakers: '{vendorcode}', '{brand}', '{model}', '{sex}', '{imgFilename}'" )
        

    sizes= sizes.replace('[', '{').replace(']', '}').replace('\'', '')

    #получаем предыдущую цену
    try:
        if sale is False:
            cursor.execute(f"SELECT currentprice FROM aviability where vendorcode='{vendorcode}'")
            lastPrice=cursor.fetchone()   
        if lastPrice is not None:
            lastPrice=str(lastPrice).replace('(','').replace(')','').replace(',','')
        else:
            lastPrice=0
    except:
        print(f"Проблемы с предыдушей ценой у {vendorcode} {str(lastPrice)}")
    try:
    #cursor.execute(f"insert into aviability (vendorcode, shopid, currentprice, previousprice, sale, sizes, link, lastchecking) values ('{vendorcode}', {shopID},    {price},    {lastPrice},    {sale},    '{sizes}',  '{url}', '{date}');")
        cursor.execute(f"""
        UPDATE  aviability SET  
        currentprice='{price}', previousprice={lastPrice}, sale={sale}, sizes='{sizes}', link='{url}', lastchecking='{date}' WHERE (vendorcode='{vendorcode}' and shopid={shopID});
        INSERT INTO aviability (vendorcode, shopid, currentprice, previousprice, sale, sizes, link, lastchecking) 
        select '{vendorcode}', {shopID},    {price},    {lastPrice},    {sale},    '{sizes}',  '{url}', '{date}'
        WHERE NOT EXISTS (SELECT 1 FROM aviability WHERE (vendorcode='{vendorcode}' and shopid={shopID}));""")
        conn.commit()
        print('Записали в aviability ' + vendorcode)
    except:
        print(f"не удалось записать в aviability: '{vendorcode}', {shopID},    {price},    {lastPrice},    {sale},    '{sizes}',  '{url}', '{date})")

    return(0)

# vendorcode='54GG3312w'
# brand='adidas'
# model='eqt ebanina 9000'
# sex='M'
# shopID='1'
# price='7000'
# sale='False'
# sizes='{40,41,42,43,44}'
# url='brandshop.ru/goods/111096/krossovki-adidas-originals-yeezy-500-supermoon-yellow'
# img='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTFzU3fo--LcptQmldIEPvzDWuvvphSt_VwNtpZ75Dt1KPL33TlmQ'
# lastPrice='5000'
# addToBD(vendorcode, brand, model, sex, price, url, img, sizes, shopID, sale,lastPrice)