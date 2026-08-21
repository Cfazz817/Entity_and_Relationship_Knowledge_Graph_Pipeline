import fitz

pdf_path = "/home/fazzin8r/dev/entity_pipeline/pdfs/Eaters_of_Children.pdf"

try:
    with fitz.open(pdf_path) as doc:
        # Check a few random pages in the middle of the book
        for page_num in [50, 51, 100]:
            page = doc[page_num]
            print(f"--- Page {page_num} ---")
            print(f"Page height: {page.rect.height}, Page width: {page.rect.width}")
            blocks = page.get_text("blocks")
            
            # Print the first 4 blocks and the last 2 blocks
            print("TOP BLOCKS:")
            for b in blocks[:4]:
                x0, y0, x1, y1, text, block_no, block_type = b
                if text.strip():
                    print(f"  y0: {y0:.1f}, y1: {y1:.1f} | Text: {repr(text.strip()[:60])}")
                    
            print("BOTTOM BLOCKS:")
            for b in blocks[-2:]:
                x0, y0, x1, y1, text, block_no, block_type = b
                if text.strip():
                    print(f"  y0: {y0:.1f}, y1: {y1:.1f} | Text: {repr(text.strip()[:60])}")
            print("\n")
except Exception as e:
    print(f"Error: {e}")
