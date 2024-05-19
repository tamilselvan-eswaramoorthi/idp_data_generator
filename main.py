import os
import uuid
from tqdm import tqdm
from pdf_generator.w2 import Create_W2 
from data_generator.w2 import W2 

data_gen = W2()
pdf_gen = Create_W2()
base_path = 'data'
num_files = 1
for i in tqdm(range(num_files)):
    file_path = os.path.join(base_path, f'w2_{uuid.uuid4()}.pdf')
    json_data = data_gen.get_data()
    bbox = pdf_gen.fill_pdf(json_data, file_path, freeze=False)
    pdf_gen.augment(bbox, file_path, file_path.replace('.pdf', '_aug.pdf'))
