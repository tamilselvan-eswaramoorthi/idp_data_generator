import cv2
import json
import fitz
from PIL import Image
import augraphy as aug
from pdf2image import convert_from_path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, IndirectObject, TextStringObject, NumberObject

from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTText, LTChar, LTAnno
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager

def combine_bounding_boxes(bounding_boxes):
    # Initialize with extreme values to find minimum and maximum coordinates
    x_min_combined, y_min_combined = float('inf'), float('inf')
    x_max_combined, y_max_combined = float('-inf'), float('-inf')

    # Iterate through each bounding box
    for bbox in bounding_boxes:
        x_min, y_min, x_max, y_max = bbox
        x_min_combined = min(x_min_combined, x_min)
        y_min_combined = min(y_min_combined, y_min)
        x_max_combined = max(x_max_combined, x_max)
        y_max_combined = max(y_max_combined, y_max)

    # Create the combined bounding box
    combined_bbox = (x_min_combined, y_min_combined, x_max_combined, y_max_combined)
    return combined_bbox

class Create_W2:
    def __init__(self):
        self.zoom = 3
        self.template_path = "static/fields/w2/w2.pdf"
        self.box_12_map = {'a': 'a_value', 'b': 'b_value', 'c': 'c_value', 'd': 'd_value'}
        self.template_bbox = self.extract_text_and_bounding_boxes(self.template_path)
        
        doc = fitz.open(self.template_path)
        self.width = doc[0].rect.width
        self.height = doc[0].rect.height
        self.resolution_factor = 2

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
        output = self.set_need_appearances_writer(output)
        filled_bbox = []

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
                        filled_bbox.append({'text': json_data['employee'][field_value], 'bbox': [ int(coord) for coord in field.get('/Rect')]})
                    
                    elif field_value in json_data['employer']:
                        field.update({NameObject('/V'): TextStringObject(json_data['employer'][field_value])})
                        field = self._change_style(field)
                        filled_bbox.append({'text': json_data['employer'][field_value], 'bbox': [ int(coord) for coord in field.get('/Rect')]})

                    elif field_value in json_data['compensation']:
                        field.update({NameObject('/V'): TextStringObject(json_data['compensation'][field_value])})
                        field = self._change_style(field)
                        filled_bbox.append({'text': json_data['compensation'][field_value], 'bbox': [ int(coord) for coord in field.get('/Rect')]})

                    elif field_value in ['a', 'b', 'c', 'd', 'a_value', 'b_value', 'c_value', 'd_value']:
                        field.update({NameObject('/V'): TextStringObject(box_12_dict[field_value])})
                        field = self._change_style(field)
                        filled_bbox.append({'text': box_12_dict[field_value], 'bbox': [ int(coord) for coord in field.get('/Rect')]})

                    elif field_value.endswith('_1') or field_value.endswith('_2'):
                        field.update({NameObject('/V'): TextStringObject(json_data['local'][field_value])})
                        field = self._change_style(field)
                        filled_bbox.append({'text': json_data['local'][field_value], 'bbox': [ int(coord) for coord in field.get('/Rect')]})

                elif field_type == '/Btn' :
                    key, value = buttons.popitem()
                    field.update({NameObject("/V"): NameObject("/"+str(value))})
        
                if freeze:
                    field.update({NameObject("/Ff"): NumberObject(1)})

            output.add_page(page)

            with open(save_path, 'wb') as output_file:
                output.write(output_file)

        bbox = self.template_bbox + filled_bbox
        return bbox

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

