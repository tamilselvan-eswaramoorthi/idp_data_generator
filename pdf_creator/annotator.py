import os
import fitz
import os.path as osp
from glob import glob
from PIL import Image
from PyPDFForm import PdfWrapper
import xml.etree.ElementTree as ET


class PDFAnnotator:
    def __init__(self) -> None:
        self.font = 'Helvetica'
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
    
    def get_height_width(self, input_path):
        doc = fitz.open(input_path)
        page = doc[0]
        width = page.rect.width
        height = page.rect.height
        return height, width

    def add_editable_fields(self, pdf_path, field_names, xywhs, max_lengths, field_types):
        new_form = PdfWrapper(pdf_path)

        height, width = self.get_height_width(input_path=pdf_path)
        for idx, (xywh, field_name, field_type) in enumerate(zip(xywhs, field_names, field_types)):
            [x, y, w, h] = xywh
            y = height - y - self.font_size

            if field_type == 'text':
                new_form.create_widget(
                    widget_type="text",
                    x=x, y=y, width=w, height=h,
                    name=field_name, page_number=1, max_length=max_lengths[idx],
                    font=self.font, font_size=self.font_size, font_color=self.font_color, border_width=self.border_width
                    )
            else:
                new_form.create_widget(
                    widget_type="checkbox",
                    x=x, y=y, width=w, height=h,
                    name=field_name, page_number=1,
                    button_style="circle", tick_color=self.font_color, border_width= self.border_width
                    )

        with open(pdf_path, "wb+") as output:
            output.write(new_form.read())

    def image_to_pdf(self, image_path, pdf_path):
        img = Image.open(image_path)
        img.save(pdf_path, "PDF", resolution=100.0, save_all=True)

    def load_annotations(self, path):

        all_annot_dict = []
        annots = sorted(glob(osp.join(path, 'Annotations/*.xml')))
        images = sorted(glob(osp.join(path, 'JPEGImages/*')))
        
        for annot_file, image_path in zip(annots, images):

            annot_dict = {}
            tree = ET.parse(annot_file)
            root = tree.getroot()

            width = int(root.find("size/width").text)
            height = int(root.find("size/height").text)

            annot_dict['image_path'] = image_path
            annot_dict['size'] = {'width': width, 'height': height}

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
                    else:
                        field_value = True

                    attributes[field_name] = field_value
                
                annot_dict['type'] = field_type
                annot_dict['coordinate'] = coordinate
                annot_dict['attributes'] = attributes
                # print (annot_dict)
            
            all_annot_dict.append(annot_dict)
        print (all_annot_dict)
        return all_annot_dict
    
    def process(self, annotation_path):
        annotations = self.load_annotations(annotation_path)
        pdf_base_path = os.path.join(annotation_path, "pdfs")
        
        os.makedirs(pdf_base_path, exist_ok = True)
        for annotation in annotations:
            image_path = annotation['image_path']
            image_name = os.path.basename(image_path)
            name, ext = os.path.splitext(image_name)
            pdf_path = os.path.join(pdf_base_path, name + '.pdf')
            self.image_to_pdf(image_path=image_path, pdf_path=pdf_path)


            


annot = PDFAnnotator()

annot.process('/home/tamilselvan/Downloads/pan')

# details = {
#     "xywhs" : [[10, 10, 100, 10]],
#     "field_names" : ['aa'],
#     "max_lengths" : [10],
#     "field_types" : ['checkbox']
#     }

# annot.add_editable_fields('updated.pdf', 'output.pdf', **details)
