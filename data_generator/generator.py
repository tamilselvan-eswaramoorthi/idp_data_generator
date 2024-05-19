import time
import math
import names
import locale
import string
import random
import secrets
import getindianname
from random_address import real_random_address

class Generator:
    def __init__(self) -> None:
        self.emails=['gmail.com','outlook.com','tutanota.com','gmx.com','yahoo.com','aol.com','mail.com','zoho.com','protonmail.com','mailerlite.com','ukr.net','mail.ru','yandex.ru']
        self.separator=['.','-','_','']
        self.adjectives = ["Tech", "Innovative", "Global", "Creative", "Dynamic", "Smart", "Agile", "Bright", "NexGen", "Fusion"]
        self.nouns = ["Solutions", "Labs", "Systems", "Tech", "Group", "Enterprises", "Innovations", "Digital", "Networks", "Ventures"]

    def get_address(self):
        address = real_random_address()
        address['address'] = address.pop('address1') + address.pop('address2')
        address.pop('coordinates')
        address['postal_code'] = address.pop('postalCode')
        return address

    def get_date(self, data_alone = True, start = '01-01-2021 00:00:00', end = '01-01-2024 00:00:00', time_format = '%d-%m-%Y %H:%M:%S'):
        prop = random.random()
        if data_alone:
            start, end, time_format = start.split(' ')[0], end.split(' ')[0], time_format.split(' ')[0]

        stime = time.mktime(time.strptime(start, time_format))
        etime = time.mktime(time.strptime(end, time_format))
        ptime = stime + prop * (etime - stime)
        return time.strftime(time_format, time.localtime(ptime))

    def get_number(self, num_digits=2, start = None, end = None, decimal = False, 
                   currency = False, currency_symbol = True, currency_seperated = True):
        if decimal:
            num_digits += decimal
        if start is None:
            start = 10**(num_digits-1)
        if end is None:
            end = (10**num_digits)-1
        num = random.randint(start, end)
        if decimal:
            num = num/(10**decimal)

        if currency:
            locale.setlocale(locale.LC_ALL, 'en_'+currency+'.UTF-8') 
            num = locale.currency(num, symbol=currency_symbol, grouping=currency_seperated, international=False)

        return num
    
    def get_name(self, first_only=False, last_only=False, gender = None, indian = False, suffix = False):

        if gender is None:
            gender = random.choice(['male', 'female'])
        
        if indian:
            if gender == 'male':
                name = getindianname.male()
            else:
                name = getindianname.female()
            if first_only:
                name = name.split(' ')[0]
            elif last_only:
                name = name.split(' ')[1]
        else:
            if first_only:
                name = names.get_first_name(gender = gender)
            elif last_only:
                name = names.get_last_name(gender = gender)
            else:
                name = names.get_full_name(gender = gender)
        
        if suffix:
            if gender == 'male':
                suffix = random.choice(['Dr. ', 'Mr. '])
            else:
                suffix = random.choice(['Dr. ', 'Miss. ', 'Mrs. '])
            name = suffix + name 
        return name
    
    def get_email(self, random_domain = False):
        """Generate a random email address."""
        domain = 'gmail.com'
        letters = string.ascii_lowercase
        cletters=string.ascii_uppercase

        if random_domain:
            domain = random.choice(self.emails)

        username = ''.join(random.choice(letters) for i in range(random.randint(5, 10) ))
        fstnm = names.get_first_name() 
        sndname = names.get_last_name()

        typ = random.randint(1, 9) 
        if typ==1:
            mail=fstnm+random.choice(self.separator)+sndname+'@'+domain
        elif typ==2:
            mail=random.choice(cletters)+random.choice(self.separator)+sndname+'@'+domain
        elif typ==3:
            mail=fstnm+random.choice(self.separator)+sndname+random.choice(self.separator)+ str(random.randint(1900,2030))+'@'+domain
        elif typ==4:
            mail=fstnm+random.choice(self.separator)+ str(random.randint(1900,2030))+'@'+domain   
        elif typ==5:
            mail=random.choice(cletters)+ sndname+random.choice(self.separator)+ str(random.randint(1960,2018)) +'@'+domain 
        elif typ==6:
            mail=fstnm+random.choice(self.separator)+ username +'@'+domain
        elif typ==7:
            mail=fstnm+ username +sndname +'@'+domain  
        elif typ==8:
            mail=sndname+ random.choice(self.separator) + username +'@'+domain 
        else:
            mail=username+ random.choice(self.separator) + fstnm  +'@'+domain
        return mail
    
    def get_company_name(self):
        typ = random.randint(1, 3) 
        if typ == 1:
            return random.choice(self.adjectives) + " " + random.choice(self.nouns)
        elif typ ==2:
            return names.get_first_name() + " " + random.choice(self.nouns)
        else:
            return names.get_first_name() + " " + random.choice(self.adjectives) + " " + random.choice(self.nouns)

    def random_alphanum(self, length: int) -> str:
        if length == 0:
            return ''
        elif length < 0:
            raise ValueError('Negative argument not allowed')
        else:
            text = secrets.token_hex(nbytes=math.ceil(length / 2))
            is_length_even = length % 2 == 0
            return text if is_length_even else text[1:]

