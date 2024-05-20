import argparse
from pdf_generator.w2 import CreateW2

def main():
    # Initialize the argument parser
    parser = argparse.ArgumentParser(description='Generate W2 PDF files.')

    # Add arguments for num_files and augment
    parser.add_argument('--base_path', type=str, required=False, default='data/', help='path where the result should be saved')
    parser.add_argument('--num_files', type=int, required=True, help='Number of W2 PDF files to generate')
    parser.add_argument('--augment', type=bool, required=False, default=True, help='Whether to augment the data (True/False)')

    # Parse the arguments
    args = parser.parse_args()

    # Use the parsed arguments
    CreateW2(base_path='data').generate_pdfs(num_files=args.num_files, augment=args.augment)

if __name__ == '__main__':
    main()
