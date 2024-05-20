from pdf_generator.w2 import CreateW2 

CreateW2(base_path='data').generate_pdfs(num_files = 100, augment=True)
