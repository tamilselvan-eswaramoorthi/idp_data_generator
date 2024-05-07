import json
from generator import Generator

class W2:
    def __init__(self) -> None:
        self.gen = Generator()
    
    def get_data(self):
        with open("fields/w2.json", 'r') as f:
            json_data = json.load(f)
        
        ## Employee
        json_data['employee']['suffix'], json_data['employee']['first_name'], json_data['employee']['last_name']  = self.gen.get_name(suffix=True).split(' ')
        address = self.gen.get_address()
        address = address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        json_data['employee']['address'] = address
        json_data['employee']['ssn'] = str(self.gen.get_number(num_digits=3)) + "-" + str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=4))

        ##Employer
        json_data['employer']['ein'] = str(self.gen.get_number(num_digits=2)) + "-" + str(self.gen.get_number(num_digits=7))
        json_data['employer']['name'] = self.gen.get_company_name()
        address = self.gen.get_address()
        address = address['address'] + '\n' + address['city'] + ', ' + address['state'] + ' ' + address['postal_code']
        json_data['employer']['address'] = address

        # json_data['compensation']['assessment_year'] = 

        return json_data
