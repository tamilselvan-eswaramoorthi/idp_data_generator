import cv2
import fitz
import numpy as np
from PIL import Image
import augraphy as aug
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, IndirectObject, TextStringObject, NumberObject

class Create_W2:
    def __init__(self):
        self.zoom = 3
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
    
    def _change_style(self, field):
        field.update({NameObject('/DA'): TextStringObject("/HelveticaLTStd 8.00 Tf 0.000 0.000 0.000 rg")}) 
        # field.update({NameObject('/Q'): TextStringObject("0")})  # 0 for left alignment
        return field

    def fill_pdf(self, json_data, save_path, freeze = False):
        box_12_dict = {}
        for key, value in self.box_12_map.items():
            box_12_dict[key] = ''
            box_12_dict[value] = ''

        for json_key, map_key in zip(json_data['compensation']["12"].keys(), list(self.box_12_map.keys())[:len(json_data['compensation']["12"])]):
            box_12_dict[map_key] = json_key
            box_12_dict[self.box_12_map[map_key]] = json_data['compensation']["12"][json_key]

        buttons = {
            "3rd_sick_pay": int(json_data['compensation']['3rd_sick_pay']),
            "retirement_plan": int(json_data['compensation']['retirement_plan']),
            "statutory_employee": int(json_data['compensation']['statutory_employee']),
        }

        output = PdfWriter()
        # output = self.set_need_appearances_writer(output)

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
                        field = self._change_style(field)
                    elif field_value in json_data['employer']:
                        field.update({NameObject('/V'): TextStringObject(json_data['employer'][field_value])})
                        field = self._change_style(field)
                    elif field_value in json_data['compensation']:
                        field.update({NameObject('/V'): TextStringObject(json_data['compensation'][field_value])})
                        field = self._change_style(field)
                    elif field_value in ['a', 'b', 'c', 'd', 'a_value', 'b_value', 'c_value', 'd_value']:
                        field.update({NameObject('/V'): TextStringObject(box_12_dict[field_value])})
                        field = self._change_style(field)
                    elif field_value.endswith('_1') or field_value.endswith('_2'):
                        field.update({NameObject('/V'): TextStringObject(json_data['local'][field_value])})
                        field = self._change_style(field)
                elif field_type == '/Btn' :
                    key, value = buttons.popitem()
                    
                    field.update({NameObject("/V"): NameObject("/"+str(value))})
                if freeze:
                    field.update({NameObject("/Ff"): NumberObject(1)})

            output.add_page(page)

            with open(save_path, 'wb') as output_file:
                output.write(output_file)

    def pdf_to_image(self, pdf_path):
        doc = fitz.open(pdf_path)
        images = []
        for page in doc:
            mat = fitz.Matrix(self.zoom, self.zoom)
            pix = page.get_pixmap(matrix = mat, alpha = False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(np.array(img))
        cv2.imwrite("image.png", images[0])
        return images

    def augment(self, pdf_path, output_path, probability=0.5):
        images = self.pdf_to_image(pdf_path)
        ink_phase = [aug.OneOf([aug.Dithering(p=probability/2),
                                aug.InkBleed(p=probability/2)], p=probability)]
        paper_phase = [aug.ColorPaper(p=probability/2),
                       aug.OneOf([aug.AugmentationSequence([
                                aug.NoiseTexturize(p=probability/2),  
                                aug.BrightnessTexturize(p=probability/2)])
                                ])]
        post_phase = [aug.Markup(p=probability),
                      aug.PageBorder(p=probability),
                      aug.SubtleNoise(p=probability),
                      aug.Jpeg(p=probability),
                    #   aug.PencilScribbles(p=probability),
                      aug.BleedThrough(p=probability)]
        pipeline = aug.AugraphyPipeline(ink_phase, paper_phase, post_phase)
        synthetic_images = [pipeline.augment(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))["output"] for image in images]
        synthetic_images = [Image.fromarray(image).convert('RGB') for image in synthetic_images]

        synthetic_images[0].save(output_path,
                                 save_all=True, 
                                 append_images=synthetic_images)
