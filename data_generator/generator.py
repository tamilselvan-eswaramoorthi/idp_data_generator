
from data_generator.utility import Generator


class DataGenerator:
    def __init__(self) -> None:
        self.data_gen = Generator()

    def get_data(self, annotation):
        def handle_static(dic, field_name, attribute):
            if attribute['static_value'] is not None:
                if len(attribute['static_value']) > 1:
                    dic[field_name] = attribute['static_value']
            return dic

        text_fields = {}
        for field in annotation['fields']:
            if field['type'] == 'textbox':
                attribute = field['attributes']
                field_name = attribute['1_field_name']
                if attribute['3_is_alphanum']:
                    if attribute['alpha_num_placement'] is None:
                        raise f"Alpha num placement is not available for {field_name}"
                    text_fields[field_name] = self.data_gen.get_alphanum(attribute['alpha_num_placement'])
                    text_fields = handle_static(text_fields, field_name, attribute)

                elif attribute['4_is_date']:
                    if attribute['date_format'] is None:
                        raise f"date format is not available for {field_name}"
                    text_fields[field_name] = self.data_gen.get_date(time_format=attribute['date_format'])
                    text_fields = handle_static(text_fields, field_name, attribute)

                elif attribute['5_is_name']:
                    if attribute['name_type'] == 'n/a':
                        raise f"Name type is not available for {field_name}"
                    first_only = False
                    last_only = False
                    suffix = False
                    gender = False
                    indian = False
                    if attribute['name_type'] == 'first_name':
                        first_only = True
                    elif attribute['name_type'] == 'last_name':
                        last_only = True
                    
                    if 'suffix' in attribute.keys():
                        if attribute['suffix'] == True:
                            suffix = True
                    if 'gender' in attribute.keys():
                        if attribute['gender'] == 'male' or attribute['gender'] == 'female':
                            gender = attribute['gender']
                    text_fields[field_name] = self.data_gen.get_name(first_only=first_only, last_only=last_only, suffix=suffix, gender=gender, indian=indian)
                    text_fields = handle_static(text_fields, field_name, attribute)
        
        return {'textbox': text_fields}