import os
import sys
import cv2
import fitz
import json
import numpy as np
from tqdm import tqdm
import os.path as osp
from glob import glob
from PIL import Image
import concurrent.futures

from pypdf import PdfReader
from PyPDFForm import PdfWrapper
import xml.etree.ElementTree as ET
from pdf2image import convert_from_path

from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTText, LTChar, LTAnno
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager


from data_generator.generator import DataGenerator 

from .augment import get_augment_pipeline
from .utils import combine_bounding_boxes, convert_xyxy_to_8_cords, flip_bbox


class PDFAnnotator:
    def __init__(self, base_path, num_workers = 1) -> None:
        self.timeout = 10
        self.num_workers = num_workers
        self.base_path = base_path
        if osp.exists(self.base_path):
            self.setup_directories()
        self.data_gen = DataGenerator()
        self.font = 'Helvetica'

        self.resolution_factor = 2
        
        self.filled_pdf_colour = (0, 0, 0)
        self.font_size = 10
        self.font_color = (0, 0, 0)
        self.border_width = -1
        self.formFontNames = {
        "Helvetica"
        "Helvetica-Bold"
        'Courier'
        'Courier-Bold'
        'Courier-Oblique'
        'Courier-BoldOblique'
        'Helvetica-Oblique'
        'Helvetica-BoldOblique'
        'Times-Roman'
        'Times-Bold'
        'Times-Italic'
        'Times-BoldItalic'
        }
        self.checkbox_style = ['check', 'cross', 'circle', 'star', 'diamond']

    def setup_directories(self):
        self.image_path = self.create_directory('images')
        self.text_path = self.create_directory('txts')
        self.json_path = self.create_directory('jsons')
        self.pdf_path = self.create_directory('pdfs')
        self.template_path = self.create_directory('templates')

    def create_directory(self, directory_name):
        path = os.path.join(self.base_path, directory_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def get_height_width(self, input_path):
        doc = fitz.open(input_path)
        page = doc[0]
        width = page.rect.width
        height = page.rect.height
        return height, width

    def convert_bbox(self, coord, height):
        x1, y1, x2, y2 = coord
        new_y1 = height - y2 - 1
        new_y2 = height - y1 - 1
                
        return [x1, new_y1, x2, new_y2]

    def add_editable_fields(self, pdf_path, annotation):
        new_form = PdfWrapper(pdf_path)

        height, width = self.get_height_width(input_path=pdf_path)
        scale_width, scale_height = width/annotation['size']['width'], height/annotation['size']['height']
        for idx, field in enumerate(annotation['fields']):
            if field['type'] == 'textbox':
                [x1, y1, x2, y2] = field['coordinate']
                [x1, y1, x2, y2] = [x1 * scale_height, y1 * scale_width, x2 * scale_height, y2 * scale_width]
                [x1, y1, x2, y2] = self.convert_bbox([x1, y1, x2, y2], height)

                [x, y, w, h] = [x1, y1, x2-x1, y2-y1]

                attributes = field['attributes']

                new_form.create_widget(
                    widget_type="text",
                    x=x, y=y, width=w, height=h,
                    name=attributes['1_field_name'], page_number=1, max_length=float(attributes['2_max_length']),
                    font=self.font, font_size = int(h-4),  font_color=self.font_color, border_width=self.border_width
                    )
     
        with open(pdf_path, "wb+") as output:
            output.write(new_form.read())
        return pdf_path

    def image_to_pdf(self, image_path, pdf_path):
        img = Image.open(image_path)
        img.save(pdf_path, "PDF", resolution=100.0, save_all=True)
        return pdf_path
    
    def pdf_to_image(self, pdf_path, size, image_path):
        """Convert PDF to image."""
        
        img = convert_from_path(pdf_path, size=(size['width'] * self.resolution_factor, size['height'] * self.resolution_factor))[0]
        img.save(image_path, 'PNG')
        return np.array(img)
    

    def load_annotations(self):

        all_annot_dict = []
        annots = sorted(glob(osp.join(self.base_path, 'Annotations/*.xml')))
        images = sorted(glob(osp.join(self.base_path, 'JPEGImages/*')))
        
        for annot_file, image_path in zip(annots, images):

            annot_dict = {}
            tree = ET.parse(annot_file)
            root = tree.getroot()

            width = int(root.find("size/width").text)
            height = int(root.find("size/height").text)

            annot_dict['image_path'] = image_path
            annot_dict['size'] = {'width': width, 'height': height}
            fields = []
            for boxes in root.iter('object'):
                field_type = boxes.find('name').text

                ymin = int(float(boxes.find("bndbox/ymin").text))
                xmin = int(float(boxes.find("bndbox/xmin").text))
                ymax = int(float(boxes.find("bndbox/ymax").text))
                xmax = int(float(boxes.find("bndbox/xmax").text))

                coordinate = [xmin, ymin, xmax, ymax]

                attributes = {}
                for attribute in boxes.iter("attribute"):
                    field_name = (attribute.find('name').text)
                    field_value = (attribute.find('value').text)
                    if field_value == "False":
                        field_value = False
                    elif field_value == "True":
                        field_value = True

                    attributes[field_name] = field_value
                
                field = {'type' : field_type, 'coordinate' : coordinate, 'attributes' : attributes}
                fields.append(field)
            annot_dict['fields'] = fields
        all_annot_dict.append(annot_dict)
        return all_annot_dict
    
    def extract_text_and_bounding_boxes(self, pdf_path):
        """Extract text and bounding boxes from a PDF file."""
        with open(pdf_path, 'rb') as fp:
            manager = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(manager, laparams=laparams)
            interpreter = PDFPageInterpreter(manager, device)
            pages = PDFPage.get_pages(fp)
            bb_text = []

            for page in pages:
                interpreter.process_page(page)
                layout = device.get_result()

                for textbox in layout:
                    if isinstance(textbox, LTText):
                        for sentence in textbox:
                            if isinstance(sentence, (LTChar, LTAnno)):
                                continue
                            text = ''
                            bbox = []
                            for letter in sentence:
                                char = letter.get_text()
                                if char == ' ':
                                    if text:
                                        bb_text.append({'text': text, 'bbox': combine_bounding_boxes(bbox)})
                                    text = ''
                                    bbox = []
                                elif char == '\n':
                                    if bbox:
                                        bb_text.append({'text': text, 'bbox': combine_bounding_boxes(bbox)})
                                    text = ''
                                    bbox = []
                                else:
                                    text += char
                                    bbox.append(letter.bbox)
        return bb_text

    def fill_pdf(self, form_fields, current_template_path, save_json_path, save_pdf_path):
        """Fill the PDF form with given data and save it."""

        pdf_dict = {}
        checkbox_fields = []

        with open(current_template_path, 'rb') as f:
            pdf = PdfReader(f)
            page = pdf.pages[0]
            annotations = page['/Annots']

            for annotation in annotations:
                field = annotation.get_object()
                field_type = field.get('/FT')
                field_value = field.get('/V')

                if field_value is not None and field_type == '/Tx':
                    pdf_dict[field_value] = field.get('/T')
                elif field_type == '/Btn':
                    checkbox_fields.append(field.get('/T'))

        #handles fields
        filler_dict = form_fields['textbox']

        # #handles checkboxes
        # filler_dict.update({field_text: field_value for field_text, field_value in zip(checkbox_fields, form_fields['button_details'].values())})

        filled_pdf = PdfWrapper(current_template_path, global_font_color=self.filled_pdf_colour, global_font=self.font).fill(filler_dict)

        with open(save_pdf_path, "wb+") as output:
            output.write(filled_pdf.read())

        with open(save_json_path, 'w') as json_write_file:
            json.dump(form_fields, json_write_file, indent=4)

        return self.extract_text_and_bounding_boxes(save_pdf_path)
    
    def generate_pdf(self, index, current_template_path, annotation, probability=0.5, augment=True, save_txt=True, draw_bb=False):
        
        """Generate the PDF with filled data, optionally apply augmentations, and save results."""
        current_name = osp.basename(current_template_path).replace('.pdf', f'_{index}')
        save_json_path = osp.join(self.json_path, current_name + '.json')
        save_pdf_path = osp.join(self.pdf_path, current_name + '.pdf')
        image_path = osp.join(self.image_path, current_name + '.png')
        text_path = osp.join(self.text_path, current_name + '.txt')

        json_data = self.data_gen.get_data(annotation)
        bboxes = self.fill_pdf(json_data, current_template_path, save_json_path, save_pdf_path)
        image = self.pdf_to_image(save_pdf_path, annotation["size"], image_path)

        if augment:
            height, width, _ = image.shape
            for bbox in bboxes:
                x1, y1, x2, y2 = bbox['bbox']
                bbox['bbox'] = flip_bbox([x1 * self.resolution_factor, y1 * self.resolution_factor, x2 * self.resolution_factor, y2 * self.resolution_factor], height)

            synthetic_images = []
            aug_pipeline = get_augment_pipeline(probability=probability)

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            synthetic_image = aug_pipeline.augment(image)["output"]
            synthetic_image = Image.fromarray(synthetic_image).convert('RGB')
            synthetic_image.save(image_path)
            synthetic_image.save(save_pdf_path)

        if save_txt:
            with open(text_path, 'w') as txt_write_file:
                for box in bboxes:
                    text, bbox = box['text'], convert_xyxy_to_8_cords(box['bbox'])
                    txt_write_file.write(','.join(map(str, bbox)) + "," + text + '\n')

        if draw_bb:
            draw_image = np.array(synthetic_images[0] if augment else image)
            for box in bboxes:
                x1, y1, x2, y2 = box['bbox']
                cv2.rectangle(draw_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), thickness=1)
            cv2.imwrite(image_path, draw_image)

    def generate_pdfs(self, num_files=5, augment=True, draw_bb=False):
        annotations = self.load_annotations()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for annotation in annotations:
                template_filename = osp.splitext(osp.basename(annotation['image_path']))[0]
                current_template_path = self.image_to_pdf(annotation['image_path'], osp.join(self.template_path, template_filename + '.pdf'))
                current_template_path = self.add_editable_fields(current_template_path, annotation)
                for i in tqdm(range(num_files)):
                    future = executor.submit(self.generate_pdf, 
                                             index = i, 
                                             current_template_path = current_template_path, 
                                             annotation = annotation, 
                                             augment = augment, 
                                             draw_bb=draw_bb)
                    try:
                        future.result(timeout=self.timeout)
                    except concurrent.futures.TimeoutError:
                        print(f"Skipping file {i} as it took more than {self.timeout} seconds to process")

