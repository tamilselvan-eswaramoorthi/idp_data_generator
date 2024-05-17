from filler.w2 import Create_W2 
from document_types.w2 import W2 

json_data = W2().get_data()
pdf = Create_W2()
pdf.fill_pdf(json_data, 'updated.pdf', freeze=False)

pdf.augment('updated.pdf', 'augmented.pdf')

