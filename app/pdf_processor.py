#!/usr/bin/env python3
"""
PDF processing module for text extraction and chapter splitting
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional
import PyPDF2
import pdfplumber

from .config import MEDIA_DIR, LOG_FILE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.chapters = []
        
    def extract_text(self) -> bool:
        """Extract text from PDF, return True if successful"""
        logger.info(f"Extracting text from {self.pdf_path}")
        
        try:
            # Try pdfplumber first (better for complex layouts)
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    self.text = "\n".join(text_parts)
                    logger.info(f"Successfully extracted {len(self.text)} characters using pdfplumber")
                    return True
            
            # Fallback to PyPDF2 if pdfplumber fails
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_parts = []
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                if text_parts:
                    self.text = "\n".join(text_parts)
                    logger.info(f"Successfully extracted {len(self.text)} characters using PyPDF2")
                    return True
                    
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
        
        logger.error("Failed to extract text - PDF may be image-based")
        return False
    
    def clean_text(self) -> str:
        """Clean extracted text for LLM context"""
        if not self.text:
            return ""
        
        logger.info("Cleaning extracted text")
        
        # Remove common PDF artifacts
        cleaned = self.text
        
        # Remove page numbers and headers/footers
        cleaned = re.sub(r'\b\d+\s*\|\s*\d+\b', '', cleaned)  # Page numbers like "1 | 2"
        cleaned = re.sub(r'^\s*\d+\s*$', '', cleaned, flags=re.MULTILINE)  # Standalone page numbers
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)  # Multiple newlines to double newlines
        cleaned = re.sub(r' +', ' ', cleaned)  # Multiple spaces to single space
        
        # Remove common PDF artifacts
        cleaned = re.sub(r'[^\w\s\.,!?;:()\[\]{}"\'-]', '', cleaned)  # Remove special characters except common punctuation
        
        # Clean up chapter headings
        cleaned = re.sub(r'CHAPTER\s+\d+', 'CHAPTER', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'Chapter\s+\d+', 'Chapter', cleaned)
        
        # Remove empty lines at start and end
        cleaned = cleaned.strip()
        
        logger.info(f"Text cleaned: {len(cleaned)} characters remaining")
        return cleaned
    
    def split_into_chapters(self) -> List[str]:
        """Split text into chapters based on common patterns"""
        if not self.text:
            return []
        
        logger.info("Splitting text into chapters")
        
        # More specific chapter patterns - only main chapters, not subsections
        chapter_patterns = [
            r'^\s*\d+\s+[A-Z][^.]*$',  # "1 What is deep learning?" (main chapters)
            r'^\s*Chapter\s+\d+\s*[:\-]?\s*[A-Z][^.]*$',  # "Chapter 1: What is deep learning?"
            r'^\s*CHAPTER\s+\d+\s*[:\-]?\s*[A-Z][^.]*$',  # "CHAPTER 1: What is deep learning?"
        ]
        
        # Patterns to ignore (preface, acknowledgments, etc.)
        ignore_patterns = [
            r'^\s*preface\s*$',  # preface
            r'^\s*acknowledgments?\s*$',  # acknowledgments
            r'^\s*about\s+this\s+book\s*$',  # about this book
            r'^\s*about\s+the\s+author\s*$',  # about the author
            r'^\s*about\s+the\s+cover\s*$',  # about the cover
            r'^\s*contents?\s*$',  # contents
            r'^\s*brief\s+contents?\s*$',  # brief contents
            r'^\s*appendix\s*$',  # appendix
            r'^\s*index\s*$',  # index
            r'^\s*conclusions?\s*$',  # conclusions
            r'^\s*references?\s*$',  # references
            r'^\s*bibliography\s*$',  # bibliography
            r'^\s*glossary\s*$',  # glossary
        ]
        
        # Find chapter boundaries
        chapter_starts = []
        chapter_titles = []
        seen_titles = set()  # To avoid duplicates
        lines = self.text.split('\n')
        
        # First pass: find all potential chapter lines
        potential_chapters = []
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Skip if this line matches ignore patterns
            should_ignore = False
            for pattern in ignore_patterns:
                if re.match(pattern, line_clean, re.IGNORECASE):
                    should_ignore = True
                    break
            
            if should_ignore:
                continue
            
            # Check if this line matches chapter patterns
            for pattern in chapter_patterns:
                if re.match(pattern, line_clean, re.IGNORECASE):
                    # Extract chapter title
                    title_match = re.search(r'^\s*\d+\s+(.+)$', line_clean)
                    if title_match:
                        title = title_match.group(1).strip()
                        # Remove page numbers and extra info
                        title = re.sub(r'\s+\d+$', '', title)  # Remove trailing page numbers
                        title = re.sub(r'\s+[A-Z][A-Z\s]*$', '', title)  # Remove trailing page references
                        
                        # Only add if we haven't seen this title before
                        if title not in seen_titles:
                            seen_titles.add(title)
                            potential_chapters.append((i, title))
                    break
        
        # Sort by line number and take the first occurrence of each chapter
        potential_chapters.sort(key=lambda x: x[0])
        
        # Take only the first 14 chapters (main chapters, not subsections)
        for i, (line_num, title) in enumerate(potential_chapters[:14]):
            chapter_starts.append(line_num)
            chapter_titles.append(title)
        
        # If no chapters found, try alternative patterns
        if not chapter_starts:
            logger.info("No main chapter patterns found, trying alternative patterns")
            # Look for numbered sections that might be chapters
            for i, line in enumerate(lines):
                line_clean = line.strip()
                # Look for patterns like "1. Title" or "1 Title"
                if re.match(r'^\s*\d+[\.\s]\s*[A-Z][^.]*$', line_clean):
                    # Make sure it's not a subsection (like 1.1, 1.2, etc.)
                    if not re.match(r'^\s*\d+\.\d+', line_clean):
                        title_match = re.search(r'^\s*\d+[\.\s]\s*(.+)$', line_clean)
                        if title_match:
                            title = title_match.group(1).strip()
                            chapter_titles.append(title)
                        else:
                            chapter_titles.append(f"Chapter {len(chapter_starts) + 1}")
                        chapter_starts.append(i)
        
        # If still no chapters found, split by large text blocks
        if not chapter_starts:
            logger.info("No chapter patterns found, splitting by content blocks")
            # Split by double newlines (paragraph breaks)
            chapters = re.split(r'\n\s*\n', self.text)
            # Filter out very short chapters
            chapters = [ch.strip() for ch in chapters if len(ch.strip()) > 100]
            chapter_titles = [f"Chapter {i+1}" for i in range(len(chapters))]
        else:
            # Split by found chapter boundaries
            chapters = []
            for i, start in enumerate(chapter_starts):
                if i == 0:
                    # First chapter starts from beginning
                    end = chapter_starts[1] if len(chapter_starts) > 1 else len(lines)
                    chapter_text = '\n'.join(lines[:end])
                else:
                    # Subsequent chapters start from previous chapter end
                    end = chapter_starts[i + 1] if i + 1 < len(chapter_starts) else len(lines)
                    chapter_text = '\n'.join(lines[start:end])
                
                if chapter_text.strip():
                    chapters.append(chapter_text.strip())
        
        # Store chapter titles for later use
        self.chapter_titles = chapter_titles
        
        logger.info(f"Split into {len(chapters)} chapters")
        for i, title in enumerate(chapter_titles):
            logger.info(f"Chapter {i+1}: {title}")
        
        return chapters
    
    def create_book_folder(self) -> str:
        """Create a meaningful folder name for the book"""
        # Get filename without extension
        filename = os.path.basename(self.pdf_path)
        base_name = os.path.splitext(filename)[0]
        
        # Clean the name for folder use
        folder_name = re.sub(r'[^\w\s-]', '', base_name)  # Remove special characters
        folder_name = re.sub(r'\s+', '_', folder_name)  # Replace spaces with underscores
        folder_name = folder_name.strip('_')  # Remove leading/trailing underscores
        
        # Create folder path
        book_folder = os.path.join(MEDIA_DIR, folder_name)
        os.makedirs(book_folder, exist_ok=True)
        
        logger.info(f"Created book folder: {book_folder}")
        return book_folder
    
    def save_chapters(self, book_folder: str, output_format: str = "txt") -> bool:
        """Save chapters to individual files"""
        if not self.chapters:
            logger.error("No chapters to save")
            return False
        
        logger.info(f"Saving {len(self.chapters)} chapters to {book_folder}")
        
        try:
            for i, chapter in enumerate(self.chapters, 1):
                # Create chapter filename with title
                if hasattr(self, 'chapter_titles') and i <= len(self.chapter_titles):
                    # Clean the title for filename use
                    title = self.chapter_titles[i-1]
                    # Remove special characters and limit length
                    clean_title = re.sub(r'[^\w\s-]', '', title)
                    clean_title = re.sub(r'\s+', '_', clean_title)
                    clean_title = clean_title.strip('_')[:50]  # Limit length
                    chapter_filename = f"{i:02d}_{clean_title}.{output_format}"
                else:
                    chapter_filename = f"chapter_{i:03d}.{output_format}"
                
                chapter_path = os.path.join(book_folder, chapter_filename)
                
                # Save chapter
                with open(chapter_path, 'w', encoding='utf-8') as f:
                    f.write(chapter)
                
                logger.info(f"Saved chapter {i}: {chapter_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving chapters: {e}")
            return False
    
    def process(self, output_format: str = "txt") -> Optional[str]:
        """Main processing method"""
        logger.info(f"Starting PDF processing: {self.pdf_path}")
        
        # Extract text
        if not self.extract_text():
            return None
        
        # Clean text
        self.text = self.clean_text()
        
        # Split into chapters
        self.chapters = self.split_into_chapters()
        
        if not self.chapters:
            logger.error("No chapters could be extracted")
            return None
        
        # Create book folder
        book_folder = self.create_book_folder()
        
        # Save chapters
        if not self.save_chapters(book_folder, output_format):
            return None
        
        logger.info(f"PDF processing completed successfully: {book_folder}")
        return book_folder 