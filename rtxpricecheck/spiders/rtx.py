import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shutil import which
import time
from scrapy import Request
import smtplib

class RtxSpider(scrapy.Spider):
    name = 'rtx'
    allowed_domains = []
    start_urls = ['https://ek.ua']
    count = 1110
    middleprice = 0

    def __init__(self):
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # makes headless browser which improwes speed
        chrome_path = which('chromedriver')
        driver = webdriver.Chrome(executable_path=chrome_path, options=chrome_options)
        driver.get("https://ek.ua")
        search_field = driver.find_element_by_xpath("//*[@id='ek-search']")
        search_field.send_keys("Asus GeForce RTX 2070 SUPER ROG STRIX OC")
        time.sleep(3)
        btn = driver.find_element_by_xpath("//div[@class='header_search_btn-submit']")
        btn.click()
        time.sleep(3)
        self.html = driver.page_source
        driver.close()

    def parse(self, response):
        if self.count == 1110:
            self.count += 1
            resp = Selector(text=self.html)
            uah_price2 = resp.xpath('//*[@id="price_1610341"]/span[1]/text()').get()
            uah_price2 = uah_price2.replace(u'\xa0', '')
            uah_price1 = resp.xpath('//*[@id="price_1610341"]/span[2]/text()').get()
            uah_price1 = uah_price1.replace(u'\xa0', '')
            middleprice = (int(uah_price1)+int(uah_price2))//2
            self.middleprice = self.middleprice+middleprice
            yield {
                "middleprice": middleprice,
            }

            nextpage = "https://bank.gov.ua/ua/markets/exchangerates"
            request = scrapy.Request(url=nextpage, callback=self.parse)
            yield request

        elif self.count == 1111:
            usd_value = response.xpath("//tbody/tr[8]/td[5]/text()").get()
            if ',' in usd_value:
                usd_value = usd_value.replace(',','.')
            usd_price = self.middleprice/float(usd_value)
            usd_price = round(usd_price, 2)
            yield {
                "usd_value":usd_value,
                "usd_price":usd_price
            }

            sender_email = str(input("Enter email you are sending from: "))
            rec_email = str(input("Enter recipient email: "))
            password = str(input('Enter your password: '))
            message = "The price is "+str(usd_price)+"$"
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, rec_email, message)




