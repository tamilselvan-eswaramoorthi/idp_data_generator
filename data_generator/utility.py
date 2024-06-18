import time
import names
import locale
import string
import random
import getindianname
from random_address import real_random_address


class Generator:
    def __init__(self) -> None:
        self.emails = [
            'gmail.com', 'outlook.com', 'tutanota.com', 'gmx.com', 'yahoo.com',
            'aol.com', 'mail.com', 'zoho.com', 'protonmail.com', 'mailerlite.com',
            'ukr.net', 'mail.ru', 'yandex.ru'
        ]
        self.separators = ['.', '-', '_', '']
        self.adjectives = [
            "Tech", "Innovative", "Global", "Creative", "Dynamic",
            "Smart", "Agile", "Bright", "NexGen", "Fusion"
        ]
        self.nouns = [
            "Solutions", "Labs", "Systems", "Tech", "Group", "Enterprises",
            "Innovations", "Digital", "Networks", "Ventures"
        ]

    def get_address(self, formatted=False, name=None, return_dict=False):
        address = real_random_address()
        address['address'] = f"{address.pop('address1')}{address.pop('address2')}"
        address['postal_code'] = address.pop('postalCode')
        address.pop('coordinates')

        if formatted:
            full_address = f"{address['address']}\n{address['city']}, {address['state']} {address['postal_code']}" if "city" in address else f"{address['address']}\n{address['state']} {address['postal_code']}"
            if name:
                full_address = f"{name}\n{full_address}"
            if return_dict:
                return full_address, address
            else:
                return full_address
        return address

    def get_date(self, date_only=True, start='01-01-2021 00:00:00', end='01-01-2024 00:00:00', time_format='%d-%m-%Y %H:%M:%S'):
        prop = random.random()
        if date_only:
            start, end, time_format = start.split(' ')[0], end.split(' ')[0], time_format.split(' ')[0]

        stime = time.mktime(time.strptime(start, time_format))
        etime = time.mktime(time.strptime(end, time_format))
        ptime = stime + prop * (etime - stime)
        return time.strftime(time_format, time.localtime(ptime))

    def get_number(self, num_digits=2, start=None, end=None, decimal_places=0, currency=False, currency_symbol=True, currency_separated=True):
        if decimal_places:
            num_digits += decimal_places
        start = start if start is not None else 10**(num_digits - 1)
        end = end if end is not None else (10**num_digits) - 1
        num = random.uniform(start, end) if decimal_places else random.randint(start, end)
        num = round(num, decimal_places)

        if currency:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Set locale for USD by default
            num = locale.currency(num, symbol=currency_symbol, grouping=currency_separated)

        return num

    def get_name(self, first_only=False, last_only=False, gender=None, indian=False, suffix=False):
        gender = gender or random.choice(['male', 'female'])

        if indian:
            name = getindianname.male() if gender == 'male' else getindianname.female()
            name_parts = name.split(' ')
            if first_only:
                name = name_parts[0]
            elif last_only:
                name = name_parts[1]
        else:
            if first_only:
                name = names.get_first_name(gender=gender)
            elif last_only:
                name = names.get_last_name()
            else:
                name = names.get_full_name(gender=gender)

        if suffix:
            suffix = 'Dr. ' if gender == 'male' else random.choice(['Dr. ', 'Miss. ', 'Mrs. '])
            name = f"{suffix}{name}"
        return name

    def get_email(self, random_domain=False):
        domain = random.choice(self.emails) if random_domain else 'gmail.com'
        username_parts = [
            ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 10))),
            names.get_first_name(),
            names.get_last_name(),
            str(random.randint(1900, 2030))
        ]
        username = ''.join([
            random.choice(username_parts[:2]) + random.choice(self.separators) + random.choice(username_parts[2:])
            for _ in range(random.randint(1, 2))
        ])
        return f"{username}@{domain}"

    def get_company_name(self):
        name_type = random.randint(1, 3)
        if name_type == 1:
            return f"{random.choice(self.adjectives)} {random.choice(self.nouns)}"
        elif name_type == 2:
            return f"{names.get_first_name()} {random.choice(self.nouns)}"
        else:
            return f"{names.get_first_name()} {random.choice(self.adjectives)} {random.choice(self.nouns)}"

    def get_alphanum(self, format:str) -> str:
        if len(format) <= 0:
            raise ValueError('Length must be a positive integer')
        alnum = ''
        for l in format:
            if l == 'n':
                alnum += random.choices(string.digits)[0]
            elif l == 'C':
                alnum += random.choices(string.ascii_uppercase)[0]
            elif l == 'c':
                alnum += random.choices(string.ascii_lowercase)[0]
        return alnum