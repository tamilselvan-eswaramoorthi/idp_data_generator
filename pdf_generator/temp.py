import fitz
from PyPDFForm import PdfWrapper

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

    def add_editable_fields(self, input_path, output_path, field_names, xywhs, max_lengths, field_types):
        new_form = PdfWrapper(input_path)

        height, width = self.get_height_width(input_path=input_path)
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
                print ('check')
                new_form.create_widget(
                    widget_type="checkbox",
                    x=x, y=y, width=w, height=h,
                    name=field_name, page_number=1,
                    button_style="circle", tick_color=self.font_color, border_width= self.border_width
                    )

        with open(output_path, "wb+") as output:
            output.write(new_form.read())

annot = PDFAnnotator()

details = {
    "xywhs" : [[10, 10, 100, 10]],
    "field_names" : ['aa'],
    "max_lengths" : [10],
    "field_types" : ['checkbox']
    }

annot.add_editable_fields('updated.pdf', 'output.pdf', **details)
