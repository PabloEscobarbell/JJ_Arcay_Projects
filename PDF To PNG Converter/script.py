import fitz
import sys

def pdf_to_png(pdf_path, output_path):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        # Iterate through each page in the PDF
        for page_number in range(len(pdf_document)):
            # Get the content of the page
            page = pdf_document.load_page(page_number)
            # Render the page to a pixmap (image)
            pixmap = page.get_pixmap()
            # Save the pixmap as a PNG file
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