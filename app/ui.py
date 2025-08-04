import os
from .config import MEDIA_DIR, load_settings, save_settings, SUPPORTED_FORMATS

def print_menu():
    """Print the main menu"""
    current_settings = load_settings()
    print("PDF Stripper - PDF Text Extraction Tool")
    print("=" * 40)
    print("Select an option:")
    print("1. Process PDF file")
    print(f"2. Change output format (currently '{current_settings.get('output_format', 'txt')}')")
    print("3. List processed books and select one")
    print("4. View chapter text")
    print("5. Select book by index")
    print("0. Exit")

def get_choice():
    """Get user choice from menu"""
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 0 <= choice <= 5:
                return choice
        except ValueError:
            pass
        print("Invalid input. Please enter a number between 0 and 5.")

def get_pdf_path():
    """Get PDF file path from user"""
    while True:
        path = input("Enter the path to the PDF file: ").strip()
        if not path:
            print("Please enter a valid path.")
            continue
        
        # Expand user path if needed
        path = os.path.expanduser(path)
        
        if not os.path.exists(path):
            print("File does not exist. Please check the path.")
            continue
        
        if not path.lower().endswith('.pdf'):
            print("File must be a PDF. Please select a .pdf file.")
            continue
        
        return path

def change_output_format():
    """Handle output format change menu"""
    current_settings = load_settings()
    current_format = current_settings.get('output_format', 'txt')
    
    print(f"\nCurrent output format: {current_format}")
    print("Available formats:")
    
    for i, fmt in enumerate(SUPPORTED_FORMATS, 1):
        marker = " (current)" if fmt == current_format else ""
        print(f"{i}. {fmt}{marker}")
    
    while True:
        try:
            choice = int(input("Select format (1-2): "))
            if 1 <= choice <= len(SUPPORTED_FORMATS):
                selected_format = SUPPORTED_FORMATS[choice - 1]
                if selected_format == current_format:
                    print("Format is already set to this option.")
                    return
                
                current_settings['output_format'] = selected_format
                if save_settings(current_settings):
                    print(f"Output format changed to '{selected_format}'")
                else:
                    print("Failed to save format setting")
                return
        except ValueError:
            pass
        print("Invalid input. Please enter a number between 1 and 2.")

def list_processed_books_simple():
    """List all processed books in the media directory (for command line)"""
    if not os.path.exists(MEDIA_DIR):
        print("No media directory found.")
        return []
    
    books = [d for d in os.listdir(MEDIA_DIR) 
             if os.path.isdir(os.path.join(MEDIA_DIR, d))]
    
    if not books:
        print("No processed books found.")
        return []
    
    print("\nProcessed books:")
    for i, book in enumerate(books, 1):
        book_path = os.path.join(MEDIA_DIR, book)
        chapter_count = len([f for f in os.listdir(book_path) 
                           if f.endswith('.txt') or f.endswith('.md')])
        print(f"{i}. {book} ({chapter_count} chapters)")
    
    return books

def list_processed_books():
    """List all processed books in the media directory and allow selection"""
    if not os.path.exists(MEDIA_DIR):
        print("No media directory found.")
        return []
    
    books = [d for d in os.listdir(MEDIA_DIR) 
             if os.path.isdir(os.path.join(MEDIA_DIR, d))]
    
    if not books:
        print("No processed books found.")
        return []
    
    print("\nProcessed books:")
    for i, book in enumerate(books, 1):
        book_path = os.path.join(MEDIA_DIR, book)
        chapter_count = len([f for f in os.listdir(book_path) 
                           if f.endswith('.txt') or f.endswith('.md')])
        print(f"{i}. {book} ({chapter_count} chapters)")
    
    # Ask if user wants to select a book
    while True:
        choice = input(f"\nSelect a book (1-{len(books)}) or press Enter to return: ").strip()
        if not choice:  # User pressed Enter
            return []
        
        try:
            book_index = int(choice)
            if 1 <= book_index <= len(books):
                selected_book = books[book_index - 1]
                print(f"\nSelected book: {selected_book}")
                
                # Show chapters for this book
                chapter_file = select_chapter(selected_book)
                if chapter_file:
                    display_chapter_text(selected_book, chapter_file)
                return []
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(books)}.")
        except ValueError:
            print("Invalid input. Please enter a number or press Enter to return.")
    
    return books

def select_book():
    """Select a book from the list of processed books"""
    books = list_processed_books()
    if not books:
        return None
    
    while True:
        try:
            choice = int(input(f"\nSelect a book (1-{len(books)}): "))
            if 1 <= choice <= len(books):
                return books[choice - 1]
        except ValueError:
            pass
        print(f"Invalid input. Please enter a number between 1 and {len(books)}.")

def select_book_by_index_from_cli(book_index):
    """Select a book by index from command line and show its chapters"""
    books = list_processed_books()
    if not books:
        return
    
    if book_index < 1 or book_index > len(books):
        print(f"Error: Book index {book_index} is out of range (1-{len(books)})")
        return
    
    selected_book = books[book_index - 1]
    print(f"Selected book: {selected_book}")
    
    # Show chapters for this book
    book_path = os.path.join(MEDIA_DIR, selected_book)
    chapter_files = [f for f in os.listdir(book_path) 
                    if f.endswith('.txt') or f.endswith('.md')]
    chapter_files.sort()
    
    if not chapter_files:
        print("No chapter files found in this book.")
        return
    
    print(f"\nChapters in '{selected_book}':")
    for i, chapter_file in enumerate(chapter_files, 1):
        print(f"{i}. {chapter_file}")
    
    # For CLI, just show the first chapter
    if chapter_files:
        first_chapter = chapter_files[0]
        print(f"\nDisplaying first chapter: {first_chapter}")
        display_chapter_text(selected_book, first_chapter)

def select_book_by_index():
    """Select a book by its index number and show its chapters"""
    books = list_processed_books()
    if not books:
        return
    
    while True:
        try:
            choice = int(input(f"\nEnter book index (1-{len(books)}): "))
            if 1 <= choice <= len(books):
                selected_book = books[choice - 1]
                print(f"\nSelected book: {selected_book}")
                
                # Show chapters for this book
                chapter_file = select_chapter(selected_book)
                if chapter_file:
                    display_chapter_text(selected_book, chapter_file)
                return
        except ValueError:
            pass
        print(f"Invalid input. Please enter a number between 1 and {len(books)}.")

def select_chapter(book_name):
    """Select a chapter from the selected book"""
    book_path = os.path.join(MEDIA_DIR, book_name)
    if not os.path.exists(book_path):
        print(f"Book directory not found: {book_path}")
        return None
    
    # Get all chapter files
    chapter_files = [f for f in os.listdir(book_path) 
                    if f.endswith('.txt') or f.endswith('.md')]
    chapter_files.sort()  # Sort to ensure consistent ordering
    
    if not chapter_files:
        print("No chapter files found in this book.")
        return None
    
    print(f"\nChapters in '{book_name}':")
    for i, chapter_file in enumerate(chapter_files, 1):
        print(f"{i}. {chapter_file}")
    
    while True:
        try:
            choice = int(input(f"\nSelect a chapter (1-{len(chapter_files)}): "))
            if 1 <= choice <= len(chapter_files):
                return chapter_files[choice - 1]
        except ValueError:
            pass
        print(f"Invalid input. Please enter a number between 1 and {len(chapter_files)}.")

def display_chapter_text(book_name, chapter_file):
    """Display the text content of the selected chapter"""
    chapter_path = os.path.join(MEDIA_DIR, book_name, chapter_file)
    
    if not os.path.exists(chapter_path):
        print(f"Chapter file not found: {chapter_path}")
        return
    
    try:
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n{'='*60}")
        print(f"Chapter: {chapter_file}")
        print(f"Book: {book_name}")
        print(f"{'='*60}")
        print(content)
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Error reading chapter file: {e}")

def view_chapter_text():
    """Main function to handle book and chapter selection and display"""
    book_name = select_book()
    if not book_name:
        return
    
    chapter_file = select_chapter(book_name)
    if not chapter_file:
        return
    
    display_chapter_text(book_name, chapter_file) 