#!/usr/bin/env python3
"""
PDF Stripper - PDF text extraction tool
Main application entry point
"""

import os
import sys
import argparse
from .config import load_settings
from .setup import ensure_venv_and_dependencies
from .pdf_processor import PDFProcessor
from .ui import print_menu, get_choice, get_pdf_path, change_output_format, list_processed_books, view_chapter_text, select_book_by_index

def process_pdf_file(pdf_path: str, output_format: str = "txt") -> bool:
    """Process a single PDF file"""
    print(f"Processing PDF: {pdf_path}")
    print(f"Output format: {output_format}")
    
    # Create processor and process the PDF
    processor = PDFProcessor(pdf_path)
    result = processor.process(output_format)
    
    if result:
        print(f"\nPDF processed successfully!")
        print(f"Output folder: {result}")
        print(f"Chapters saved: {len(processor.chapters)}")
        return True
    else:
        print("\nFailed to process PDF")
        print("The PDF may be image-based or corrupted")
        return False

def main():
    """Main application function"""
    # Ensure dependencies are installed
    ensure_venv_and_dependencies()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='PDF Stripper - PDF Text Extraction Tool')
    parser.add_argument('pdf_file', nargs='?', help='Path to PDF file to process')
    parser.add_argument('--format', '-f', choices=['txt', 'md'], default='txt',
                       help='Output format (default: txt)')
    parser.add_argument('--list', '-l', action='store_true', 
                       help='List processed books and exit')
    parser.add_argument('--view', '-v', nargs=2, metavar=('BOOK', 'CHAPTER'),
                       help='View specific chapter (e.g., --view "Book_Name" "chapter_001.txt")')
    parser.add_argument('--book', '-b', type=int, metavar='INDEX',
                       help='Select book by index and view a chapter')
    
    args = parser.parse_args()

    # Handle list command
    if args.list:
        # For command line, just list without prompting for selection
        from .ui import list_processed_books_simple
        list_processed_books_simple()
        return

    # Handle view command
    if args.view:
        book_name, chapter_file = args.view
        from .ui import display_chapter_text
        display_chapter_text(book_name, chapter_file)
        return

    # Handle book selection by index
    if args.book:
        from .ui import select_book_by_index_from_cli
        select_book_by_index_from_cli(args.book)
        return

    # Handle direct PDF processing
    if args.pdf_file:
        if not os.path.exists(args.pdf_file):
            print(f"Error: File '{args.pdf_file}' does not exist")
            sys.exit(1)
        
        if not args.pdf_file.lower().endswith('.pdf'):
            print("Error: File must be a PDF")
            sys.exit(1)
        
        success = process_pdf_file(args.pdf_file, args.format)
        sys.exit(0 if success else 1)

    # Interactive mode
    while True:
        # Show menu and get user choice
        print_menu()
        choice = get_choice()

        if choice == 0:
            print("Goodbye!")
            return
        
        elif choice == 1:
            # Process PDF file
            pdf_path = get_pdf_path()
            settings = load_settings()
            output_format = settings.get('output_format', 'txt')
            
            process_pdf_file(pdf_path, output_format)
        
        elif choice == 2:
            # Change output format
            change_output_format()
        
        elif choice == 3:
            # List processed books
            list_processed_books()
        
        elif choice == 4:
            # View chapter text
            view_chapter_text()
        
        elif choice == 5:
            # Select book by index
            select_book_by_index()
        
        print("\n" + "="*40 + "\n")

if __name__ == "__main__":
    main() 