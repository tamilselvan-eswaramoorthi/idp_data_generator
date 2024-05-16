import json
import random 
from generator import Generator

class W2:
    def __init__(self) -> None:
        self.gen = Generator()
        self.json_path = "fields/w2/w2.json"
        self.possible_12 =  ['A', 'AA', 'B', 'BB', 'C', 'D', 'E', 'EE',
                             'F', 'FF', 'G', 'GG', 'H', 'HH', 'II', 'J',
                             'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 
                             'V', 'W', 'Y', 'Z']
    
    def get_data(self):
        with open(self.json_path, 'r') as f:
            json_data = json.load(f)
        
        ## Employee
        json_data['employee']['suffix'], json_data['employee']['first_name'], json_data['employee']['last_name']  = self.gen.get_name(suffix=True).split(' ')
        address = self.gen.get_address()
        employee_state = address['state']
        if "city" in address.keys():
            address = address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        else:
            address = address['address'] + '\n' + address['state'] + ' ' + address['postal_code']

        json_data['employee']['address'] = address
        json_data['employee']['ssn'] = str(self.gen.get_number(num_digits=3)) + "-" + str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=4))
        json_data['employee']['control_number'] = self.gen.random_alphanum(random.choice(range(6, 10)))
        
        ##Employer
        json_data['employer']['ein'] = str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=7))
        employer_name = self.gen.get_company_name()
        address = self.gen.get_address()
        if "city" in address.keys():
            address = employer_name + "\n" + address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        else:
            address = employer_name + "\n" + address['address'] + '\n' + address['state'] + ' ' + address['postal_code']
        
        json_data['employer']['name_address'] = address

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
        
        for idx in range(1, random.choice([2, 3])):
            json_data['local']['state_'+str(idx)] = employee_state.upper()
            json_data['local']['state_ein_'+str(idx)] = str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=7))
            json_data['local']['state_wages_'+str(idx)] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            json_data['local']['state_tax_'+str(idx)] = "{:,.2f}".format(float(json_data['local']['state_wages_'+str(idx)].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
            json_data['local']['local_wages_'+str(idx)] = self.gen.get_number(num_digits=random.choice(range(3, 6, 1)), decimal=2, currency="US", currency_symbol = False)
            json_data['local']['local_tax_'+str(idx)] = "{:,.2f}".format(float(json_data['local']['local_wages_'+str(idx)].replace(',', ''))*(random.choice(range(1, 20, 2))/100))
                    
        return json_data
