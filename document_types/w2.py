import json
import random 
from generator import Generator

class W2:
    def __init__(self) -> None:
        self.gen = Generator()
        self.possible_12 =  ['A', 'AA', 'B', 'BB', 'C', 'D', 'E', 'EE',
                             'F', 'FF', 'G', 'GG', 'H', 'HH', 'II', 'J',
                             'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 
                             'V', 'W', 'Y', 'Z']
    
    def get_data(self):
        with open("fields/w2.json", 'r') as f:
            json_data = json.load(f)
        
        ## Employee
        json_data['employee']['suffix'], json_data['employee']['first_name'], json_data['employee']['last_name']  = self.gen.get_name(suffix=True).split(' ')
        address = self.gen.get_address()
        employee_state = address['state']
        address = address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        json_data['employee']['address'] = address
        json_data['employee']['ssn'] = str(self.gen.get_number(num_digits=3)) + "-" + str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=4))
        json_data['employee']['control_number'] = self.gen.random_alphanum(random.choice(range(6, 10)))
        
        ##Employer
        json_data['employer']['ein'] = str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=7))
        json_data['employer']['name'] = self.gen.get_company_name()
        address = self.gen.get_address()
        address = address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        json_data['employer']['address'] = address

        json_data['compensation']['assessment_year'] = random.choice(range(2015, 2025, 1))

        json_data['compensation']['wages'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
        json_data['compensation']['federal_tax_withheld'] = "{:,.2f}".format(float(json_data['compensation']['wages'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
        json_data['compensation']['ss_wages'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
        json_data['compensation']['ss_tax_withheld'] = "{:,.2f}".format(float(json_data['compensation']['ss_wages'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))

        json_data['compensation']['medicare_wages'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
        json_data['compensation']['medicare_tax_withheld'] = "{:,.2f}".format(float(json_data['compensation']['medicare_wages'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))

        typ = random.randint(1, 9) 
        if typ==1:
            json_data['compensation']['ss_tips'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            json_data['compensation']['allocated_tips'] = "{:,.2f}".format(float(json_data['compensation']['ss_tips'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
            json_data['compensation']['dependent_care_benefits'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            json_data['compensation']['nonqualified_plans'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)

        bool_list = [False]*3
        if random.randint(1, 2)==1:
            bool_list[random.randint(0, 2)] = True
        json_data['compensation']['statutory_employee'], json_data['compensation']['retirement_plan'], json_data['compensation']['3rd_sick_pay'] = bool_list
        
        json_data['compensation']['12'] = {}
        for _ in range(random.randint(0, 4)):
            key = random.choice(self.possible_12)
            json_data['compensation']['12'][key] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
        all_details = []
        for _ in range(random.choice(range(0, 2))):
            local_details = {}
            local_details['state'] = employee_state.upper()
            local_details['state_ein'] = str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=7))
            local_details['state_wages'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            local_details['state_income_tax'] = "{:,.2f}".format(float(local_details['state_wages'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
            local_details['local_wages'] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            local_details['local_income_tax'] = "{:,.2f}".format(float(local_details['local_wages'].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
            all_details.append(local_details)
        json_data['local'] = all_details
        return json_data
