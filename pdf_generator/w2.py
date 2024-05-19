import cv2
import json
import fitz
from PIL import Image
import augraphy as aug
from pdf2image import convert_from_path

from pypdf import PdfReader
from PyPDFForm import PdfWrapper

from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTText, LTChar, LTAnno
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager

from .utils import combine_bounding_boxes

class Create_W2:
    def __init__(self):
        self.zoom = 3
        self.template_path = "static/fields/w2/w2.pdf"
        self.box_12_map = {'a': 'a_value', 'b': 'b_value', 'c': 'c_value', 'd': 'd_value'}        
        doc = fitz.open(self.template_path)
        self.width = doc[0].rect.width
        self.height = doc[0].rect.height
        self.resolution_factor = 2
        self.filled_pdf_colour = (0, 0, 0)
        self.filled_pdf_fold = 'Helvetica'

    def extract_text_and_bounding_boxes(self, pdf_path):
        with open(pdf_path, 'rb') as fp:
            manager = PDFResourceManager()
            laparams = LAParams()
            dev = PDFPageAggregator(manager, laparams=laparams)
            interpreter = PDFPageInterpreter(manager, dev)
            pages = PDFPage.get_pages(fp)
            bb_text = []
            for page in pages:
                interpreter.process_page(page)
                layout = dev.get_result()
                for textbox in layout:
                    if isinstance(textbox, LTText):
                        for sentence in textbox:
                            if isinstance(sentence, LTChar) or isinstance(sentence, LTAnno):
                                continue
                            text = ''
                            bbox = []
                            for letter in sentence:
                                char = letter.get_text()
                                if char == ' ':
                                    if text == '':
                                        continue
                                    if len(bbox):
                                        bb_text.append({'text' : text, 'bbox': combine_bounding_boxes(bbox)})
                                    text = ''
                                    bbox = []
                                else:
                                    if char == '\n':
                                        if len(bbox):
                                            bb_text.append({'text' : text, 'bbox': combine_bounding_boxes(bbox)})
                                        text = ''
                                        bbox = []
                                    else:
                                        text += char
                                        bbox.append(letter.bbox)
        return bb_text
    
    def fill_pdf(self, json_data, save_path):
        box_12_dict = {}
        for key, value in self.box_12_map.items():
            box_12_dict[key] = ''
            box_12_dict[value] = ''

        for json_key, map_key in zip(json_data['compensation']["12"].keys(), list(self.box_12_map.keys())[:len(json_data['compensation']["12"])]):
            box_12_dict[map_key] = json_key
            box_12_dict[self.box_12_map[map_key]] = json_data['compensation']["12"][json_key]

        buttons = {
            "3rd_sick_pay": bool(json_data['compensation']['3rd_sick_pay']),
            "retirement_plan": bool(json_data['compensation']['retirement_plan']),
            "statutory_employee": bool(json_data['compensation']['statutory_employee']),
        }

        pdf_dict = {}
        with open(self.template_path, 'rb') as f:
            pdf = PdfReader(f)
            page = pdf.pages[0]
            annotations = page['/Annots']
            for annotation in annotations:
                field = annotation.get_object()
                field_type = field.get('/FT')
                field_value = field.get('/V')
                if field_value is not None and field_type == '/Tx':
                    pdf_dict[field.get('/V')] = field.get('/T')
                elif field_type == '/Btn' :
                    key, value = buttons.popitem()
                    pdf_dict[value] = field.get('/T')

        filler_dict = {}
        for field_value, field_text in pdf_dict.items():
            if isinstance(field_value, bool):
                filler_dict[field_text] = field_value
            elif field_value in json_data['employee']:
                filler_dict[field_text] = json_data['employee'][field_value]
            elif field_value in json_data['employer']:
                filler_dict[field_text] = json_data['employer'][field_value]
            elif field_value in json_data['compensation']:
                filler_dict[field_text] = json_data['compensation'][field_value]
            elif field_value in ['a', 'b', 'c', 'd', 'a_value', 'b_value', 'c_value', 'd_value']:
                filler_dict[field_text] = box_12_dict[field_value]
            elif field_value.endswith('_1') or field_value.endswith('_2'):
                filler_dict[field_text] = json_data['local'][field_value]
            else:
                raise("no field found")


        filled_pdf = PdfWrapper(self.template_path, 
                                global_font_color=self.filled_pdf_colour, 
                                global_font=self.filled_pdf_fold).fill(filler_dict)

        with open(save_path, "wb+") as output:
            output.write(filled_pdf.read())

        return self.extract_text_and_bounding_boxes(save_path)

    def pdf_to_image(self, pdf_path):
        image_save_path = pdf_path.replace('.pdf', '.png')
        images_pil = convert_from_path(pdf_path, size = (self.width*self.resolution_factor, self.height*self.resolution_factor))
        images = []
        for img in images_pil:
            img.save(image_save_path, 'PNG')
            img = cv2.imread(image_save_path)
            images.append(img)
        return images

    def flip_bbox(self, bbox, height):
        shift = int((bbox[3] - bbox[1]) * 0.1)
        bbox[0] = bbox[0] - 1
        bbox[1] = height - bbox[1] - shift
        bbox[2] = bbox[2] + 1
        bbox[3] = height - bbox[3] - shift
        return bbox

    def augment(self, bboxes, pdf_path, output_path, probability=0.5):
        images = self.pdf_to_image(pdf_path)

        for idx in range(len(bboxes)):
            [x1, y1, x2, y2] = bboxes[idx]['bbox']
            bboxes[idx]['bbox'] = self.flip_bbox([x1* self.resolution_factor,
                                                  y1* self.resolution_factor, 
                                                  x2* self.resolution_factor, 
                                                  y2* self.resolution_factor], images[0].shape[0])

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
                      aug.BleedThrough(p=probability)]
        pipeline = aug.AugraphyPipeline(ink_phase, paper_phase, post_phase)
        synthetic_images = [pipeline.augment(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))["output"] for image in images]
        synthetic_images = [Image.fromarray(image).convert('RGB') for image in synthetic_images]
        if len(synthetic_images) == 1:
            synthetic_images[0].save(output_path)
        else:
            synthetic_images[0].save(output_path,
                                    save_all=True, 
                                    append_images=synthetic_images)

        with open(pdf_path.replace('.pdf', '.json'), 'w') as json_write_file:
            json.dump(bboxes, json_write_file, indent=4)

