# PDF Stripper - PDF Text Extraction Tool

A Python-based tool for extracting and processing text from PDF files, specifically designed for creating LLM context from books and documents.

## Features

- **PDF Text Extraction**: Extract text from PDF files using multiple methods (pdfplumber and PyPDF2)
- **Intelligent Chapter Splitting**: Automatically detect and split only main chapters (ignores preface, acknowledgments, subsections, appendix, index)
- **Smart Chapter Naming**: Chapters are named with numbers and descriptive titles (e.g., "01_What_is_deep_learning.txt")
- **Text Cleaning**: Clean extracted text for optimal LLM context usage
- **Progress Logging**: Detailed logging of all operations
- **Multiple Output Formats**: Support for TXT and MD output formats
- **Book Management**: List and manage processed books

## Requirements

- Python 3.11+
- macOS (designed for OS X)
- PDF files with extractable text (not image-based PDFs)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-stripper
```

2. Run the application (this will automatically set up the virtual environment):
```bash
./pdf-stripper
```

The first run will:
- Create a Python virtual environment
- Install required dependencies
- Start the application

## Usage

### Command Line Usage

The application can be used in two ways:

#### Direct PDF Processing
```bash
./pdf-stripper path/to/file.pdf
./pdf-stripper path/to/file.pdf --format md
./pdf-stripper --list
./pdf-stripper --view "Book_Name" "chapter_001.txt"
./pdf-stripper --book 1
```

**Options:**
- `pdf_file` - Path to PDF file to process
- `--format, -f {txt,md}` - Output format (default: txt)
- `--list, -l` - List processed books and exit
- `--view, -v BOOK CHAPTER` - View specific chapter text
- `--book, -b INDEX` - Select book by index and view first chapter
- `--help, -h` - Show help message

#### Interactive Mode
Run without arguments to use the interactive menu:

```bash
./pdf-stripper
```

### Main Menu

The interactive application provides a simple menu interface:

1. **Process PDF file** - Extract text from a PDF and split into chapters
2. **Change output format** - Switch between TXT and MD output formats
3. **List processed books and select one** - View all books and select one to view chapters
4. **View chapter text** - Select a book and chapter to display its text
5. **Select book by index** - Choose a book by its index number and view a chapter
0. **Exit** - Quit the application

### Processing a PDF

1. Select option 1 from the main menu
2. Enter the full path to your PDF file
3. The application will:
   - Extract text from the PDF
   - Clean the text for LLM context
   - Split the text into chapters
   - Create a folder in the `media` directory
   - Save each chapter as a separate file

### Output Structure

Processed books are saved in the `media` directory with the following structure:

```
media/
├── Book_Title_1/
│   ├── chapter_001.txt
│   ├── chapter_002.txt
│   └── ...
└── Book_Title_2/
    ├── chapter_001.txt
    ├── chapter_002.txt
    └── ...
```

## Configuration

Settings are stored in `settings.json` and include:
- Output format preference (txt/md)

## Logging

Logs are written to `logs/pdf-stripper.log`

## Limitations

- **Image-based PDFs**: Cannot extract text from PDFs that contain only images
- **Complex Layouts**: May have issues with very complex document layouts
- **Large Files**: Very large PDFs may take longer to process

## Troubleshooting

### "Failed to extract text" Error
- The PDF may be image-based or corrupted
- Try a different PDF file
- Check the log file for detailed error information

### Virtual Environment Issues
- Delete the `venv` folder and run `./pdf-stripper` again
- Ensure Python 3.11+ is installed

### Permission Issues
- Make sure the `pdf-stripper` script is executable: `chmod +x pdf-stripper`
- Check write permissions for the `media` and `logs` directories

## License

MIT
