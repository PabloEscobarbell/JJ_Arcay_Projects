import fitz
import sys

def pdf_to_png(pdf_path, output_path):
    try:
        pdf_document = fitz.open(pdf_path)
        
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            pixmap = page.get_pixmap() # Render the page to a pixmap (image)
            output_file = f"{output_path}/page_{page_number + 1}.png"
            pixmap.save(output_file)
            
        # Close the PDF document
        pdf_document.close()
    except Exception as e:
        sys.exit(f"Error: {e}")
        
    
# Main Script
try:
    pdf_path = input("Enter the path to the PDF file: ")
    pdf_path = pdf_path.strip('"')
    pdf_path = pdf_path.strip("'")
    pdf_path = fr"{pdf_path}"

    output_path = input("Enter the output directory for PNG files: ")
    output_path = output_path.strip('"')
    output_path = output_path.strip("'")
    output_path = fr"{output_path}"

    pdf_to_png(pdf_path, output_path)
except Exception as e:
    sys.exit(f"Error: {e}")