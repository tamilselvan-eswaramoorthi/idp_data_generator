import cv2
import json
import fitz
import numpy as np
from PIL import Image
from pdf2image import convert_from_path

from pypdf import PdfReader
from PyPDFForm import PdfWrapper

from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTText, LTChar, LTAnno
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager

from data_generator.w2 import W2

from .augment import get_augment_pipeline
from .utils import combine_bounding_boxes, convert_xyxy_to_8_cords

class CreateW2:
    def __init__(self):
        self.zoom = 3
        self.template_path = "static/fields/w2.pdf"
        self.box_12_map = {'a': 'a_value', 'b': 'b_value', 'c': 'c_value', 'd': 'd_value'}
        self.doc = fitz.open(self.template_path)
        self.width = self.doc[0].rect.width
        self.height = self.doc[0].rect.height
        self.resolution_factor = 2
        self.filled_pdf_colour = (0, 0, 0)
        self.filled_pdf_font = 'Helvetica'
        self.data_gen = W2()

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

    def fill_pdf(self, form_fields, save_path, save_json=True):
        """Fill the PDF form with given data and save it."""
        fields = form_fields['field_details']
        pdf_dict = {}
        checkbox_fields = []

        with open(self.template_path, 'rb') as f:
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


        #handles checkboxes
        filler_dict = {field_text: field_value for field_text, field_value in zip(checkbox_fields, form_fields['button_details'].values())}
        #handles fields
        filler_dict.update({field_text: fields[field_value] for field_value, field_text in pdf_dict.items() if field_value in fields})

        filled_pdf = PdfWrapper(self.template_path, global_font_color=self.filled_pdf_colour, global_font=self.filled_pdf_font).fill(filler_dict)

        with open(save_path, "wb+") as output:
            output.write(filled_pdf.read())

        if save_json:
            json_path = save_path.replace('.pdf', '.json')
            with open(json_path, 'w') as json_write_file:
                json.dump(form_fields, json_write_file, indent=4)

        return self.extract_text_and_bounding_boxes(save_path)

    def pdf_to_image(self, pdf_path, save_png=True):
        """Convert PDF to images."""
        images_pil = convert_from_path(pdf_path, size=(self.width * self.resolution_factor, self.height * self.resolution_factor))
        images = []
        image_paths = []

        for i, img in enumerate(images_pil):
            image_save_path = pdf_path.replace('.pdf', f'_{i}.png')
            if save_png:
                img.save(image_save_path, 'PNG')
            images.append(np.array(img))
            image_paths.append(image_save_path)

        return images, image_paths

    def flip_bbox(self, bbox, height):
        """Flip bounding boxes vertically."""
        shift = int((bbox[3] - bbox[1]) * 0.1)
        bbox[0] -= 1
        bbox[1] = height - bbox[1] - shift
        bbox[2] += 1
        bbox[3] = height - bbox[3] - shift
        return bbox

    def generate_pdf(self, output_path, probability=0.5, augment=True, save_png=True, save_txt=True, draw_bb=False):
        """Generate the PDF with filled data, optionally apply augmentations, and save results."""
        pdf_path = output_path + '.pdf'
        json_data = self.data_gen.get_data()
        bboxes = self.fill_pdf(json_data, pdf_path)
        images, image_paths = self.pdf_to_image(pdf_path)

        if augment:
            height, width, _ = images[0].shape
            for bbox in bboxes:
                x1, y1, x2, y2 = bbox['bbox']
                bbox['bbox'] = self.flip_bbox([x1 * self.resolution_factor, y1 * self.resolution_factor, x2 * self.resolution_factor, y2 * self.resolution_factor], height)

            synthetic_images = []
            aug_pipeline = get_augment_pipeline(probability=probability)

            for idx, image in enumerate(images):
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                synthetic_image = aug_pipeline.augment(image)["output"]
                synthetic_image = Image.fromarray(synthetic_image).convert('RGB')
                synthetic_images.append(synthetic_image)
                if save_png:
                    aug_image_path = pdf_path.replace('.pdf', f'_{idx}.png')
                    synthetic_image.save(aug_image_path)

            synthetic_images[0].save(pdf_path, save_all=True, append_images=synthetic_images[1:])

        if save_txt:
            txt_path = pdf_path.replace('.pdf', '.txt')
            with open(txt_path, 'w') as txt_write_file:
                for box in bboxes:
                    text, bbox = box['text'], convert_xyxy_to_8_cords(box['bbox'])
                    txt_write_file.write(','.join(map(str, bbox)) + "," + text + '\n')

        if draw_bb:
            draw_image = np.array(synthetic_images[0] if augment else images[0])
            for box in bboxes:
                x1, y1, x2, y2 = box['bbox']
                cv2.rectangle(draw_image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), thickness=1)
            cv2.imwrite(image_paths[0], draw_image)
