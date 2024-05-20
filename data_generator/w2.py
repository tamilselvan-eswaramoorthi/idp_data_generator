import random 
from data_generator.generator import Generator

class W2:
    def __init__(self) -> None:
        self.gen = Generator()
        self.possible_12 =  ['A', 'AA', 'B', 'BB', 'C', 'D', 'E', 'EE',
                             'F', 'FF', 'G', 'GG', 'H', 'HH', 'II', 'J',
                             'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 
                             'V', 'W', 'Y', 'Z']

    def get_data(self):
        employee_details, employee_state = self.populate_employee()
        employer_details = self.populate_employer()
        compensation_details = self.populate_compensation()
        local_details = self.populate_local(employee_state)
        
        return_dict =  {
            "field_details": {**employee_details, **employer_details, **compensation_details, **local_details},
            "button_details": self.generate_button_states()
        }

        return return_dict

    def populate_employee(self):
        suffix, first_name, last_name = self.gen.get_name(suffix=True).split(' ')
        full_address, address = self.gen.get_address(formatted=True, return_dict = True)
        return {
            'suffix': suffix,
            'first_name': first_name,
            'last_name': last_name,
            'employee_address': full_address,
            'ssn': self.generate_ssn(),
            'control_number': self.gen.random_alphanum(random.choice(range(6, 10)))
        }, address['state']

    def populate_employer(self):
        employer_name = self.gen.get_company_name()
        full_address = self.gen.get_address(formatted=True, name = employer_name)
        
        return {
            'ein': self.generate_ein(),
            'employer_name_address': full_address
        }

    def populate_compensation(self):
        wages = self.generate_random_currency_value()
        ss_wages = self.generate_random_currency_value()
        medicare_wages = self.generate_random_currency_value()
        
        optional_fields = self.populate_optional_compensation_fields()

        mandatory_fields = {
            'assessment_year': random.choice(range(2015, 2025)),
            'wages': wages,
            'federal_tax_withheld': self.calculate_tax(wages),
            'ss_wages': ss_wages,
            'ss_tax_withheld': self.calculate_tax(ss_wages),
            'medicare_wages': medicare_wages,
            'medicare_tax_withheld': self.calculate_tax(medicare_wages)
        }

        section_12_fields = self.generate_compensation_12()
    
        return {**optional_fields, **mandatory_fields, **section_12_fields} 

    def populate_local(self, employee_state):        
        local_details = {}
        for idx in range(1, random.choice([2, 3])):
            state_wages = self.generate_random_currency_value()
            local_wages = self.generate_random_currency_value()
            
            local_details[f'state_{idx}'] = employee_state.upper()
            local_details[f'state_ein_{idx}'] = self.generate_ein()
            local_details[f'state_wages_{idx}'] = state_wages
            local_details[f'state_tax_{idx}'] = self.calculate_tax(state_wages)
            local_details[f'local_wages_{idx}'] = local_wages
            local_details[f'local_tax_{idx}'] = self.calculate_tax(local_wages)
            local_details[f'locality_{idx}'] = ''
        return local_details
    
    def generate_ssn(self):
        return f"{self.gen.get_number(num_digits=3)}-{self.gen.get_number(num_digits=2)}-{self.gen.get_number(num_digits=4)}"

    def generate_ein(self):
        return f"{self.gen.get_number(num_digits=2)}-{self.gen.get_number(num_digits=7)}"

    def generate_random_currency_value(self):
        return self.gen.get_number(num_digits=random.choice(range(3, 6)), decimal_places=2, currency="US", currency_symbol=False)

    def calculate_tax(self, amount):
        amount_float = float(amount.replace(',', ''))
        return "{:,.2f}".format(amount_float * (random.choice(range(1, 20, 2)) / 100))

    def generate_compensation_12(self):
        comp_12 = {'a': '', 'a_value': '', 'b': '', 'b_value': '', 'c': '', 'c_value': '', 'd': '', 'd_value': ''}
        available_keys = ['a', 'b', 'c', 'd']
        
        for i in range(random.randint(0, 4)):
            key = available_keys[i]
            value_key = f"{key}_value"
            comp_12[key] = random.choice(self.possible_12)
            comp_12[value_key] = self.generate_random_currency_value()
        
        return comp_12

    def populate_optional_compensation_fields(self):
        optional_fields = {}
        typ = random.randint(1, 9)
        if typ == 1:
            optional_fields['ss_tips'] = self.generate_random_currency_value()
            optional_fields['allocated_tips'] = self.calculate_tax(optional_fields['ss_tips'])
            optional_fields['dependent_care_benefits'] = self.generate_random_currency_value()
            optional_fields['nonqualified_plans'] = self.generate_random_currency_value()
        else:
            optional_fields['ss_tips'] = optional_fields['allocated_tips'] = optional_fields['dependent_care_benefits'] = optional_fields['nonqualified_plans'] = ''
        
        return optional_fields 
    
    def generate_button_states(self):
        button_states = {}
        button_states['statutory_employee'] = random.choice([True, False])
        button_states['retirement_plan'] = random.choice([True, False])
        button_states['3rd_sick_pay'] = random.choice([True, False])
        return button_states
