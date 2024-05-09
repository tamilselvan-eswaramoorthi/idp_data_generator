from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject

class Create_W2:
    def __init__(self):
        self.template_path = "fields/w2/w2.pdf"
        self.box_12_map = {'a': 'a_value', 'b': 'b_value', 'c': 'c_value', 'd': 'd_value'}
        
    def set_need_appearances_writer(self, writer: PdfWriter):
        try:
            catalog = writer._root_object
            if "/AcroForm" not in catalog:
                writer._root_object.update({NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})
            need_appearances = NameObject("/NeedAppearances")
            writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
            return writer

        except Exception as e:
            return writer

    def fill_pdf(self, json_data, save_path):
        box_12_dict = {}
        for key, value in self.box_12_map.items():
            box_12_dict[key] = ''
            box_12_dict[value] = ''

        for json_key, map_key in zip(json_data['compensation']["12"].keys(), list(self.box_12_map.keys())[:len(json_data['compensation']["12"])]):
            box_12_dict[map_key] = json_key
            box_12_dict[self.box_12_map[map_key]] = json_data['compensation']["12"][json_key]

        output = PdfWriter()
        output = self.set_need_appearances_writer(output)

        with open(self.template_path, 'rb') as f:
            pdf = PdfReader(f)
            page = pdf.pages[0]
            annotations = page['/Annots']
            for annotation in annotations:
                field = annotation.get_object()
                field_type = field.get('/FT')
                field_value = field.get('/V')
                if field_value is not None and field_type == '/Tx':
                    if field_value in json_data['employee']:
                        field.update({NameObject('/V'): TextStringObject(json_data['employee'][field_value])})
                        field.update({NameObject('/Q'): TextStringObject("0")})  # 0 for left alignment
                        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")}) 
                    elif field_value in json_data['employer']:
                        field.update({NameObject('/V'): TextStringObject(json_data['employer'][field_value])})
                        field.update({NameObject('/Q'): TextStringObject("0")})  # 0 for left alignment
                        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")}) 
                    elif field_value in json_data['compensation']:
                        field.update({NameObject('/V'): TextStringObject(json_data['compensation'][field_value])})
                        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")})
                    elif field_value in ['a', 'b', 'c', 'd', 'a_value', 'b_value', 'c_value', 'd_value']:
                        field.update({NameObject('/V'): TextStringObject(box_12_dict[field_value])})
                        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")})  
                    elif field_value.endswith('_1') or field_value.endswith('_2'):
                        field.update({NameObject('/V'): TextStringObject(json_data['local'][field_value])})
                        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")})  
            output.add_page(page)

            with open(save_path, 'wb') as output_file:
                output.write(output_file)