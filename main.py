import os
import uuid
from tqdm import tqdm
from pdf_generator.w2 import Create_W2 

pdf_gen = Create_W2()
base_path = 'data'
num_files = 1
for i in tqdm(range(num_files)):
    file_path = os.path.join(base_path, f'w2_{uuid.uuid4()}')
    pdf_gen.generate_pdf(file_path, augment=False)
