
"""

This file defines abstract and concrete classes for handling input processing,
specifically for extracting text from different file types. It includes an
abstract base class 'Input' and a concrete implementation 'PDFInput' for
handling PDF files.

"""


from typing import Any
from abc import ABC, abstractmethod

import PyPDF2


class Input(ABC):
    """
    Abstract base class for input processing.
    This class defines the structure for handling various types of input
    and extracting text from them.
    """

    def __init__(self, file_name: str):
        """
        Initialize the Input object with a file name.

        Args:
            file_name (str): The name of the input file.
        """
        self.file_name = file_name

    @abstractmethod
    def get_text(self) -> str:
        """
        Abstract method to extract text from the input file.

        Returns:
            str: The extracted text from the input file.
        """
        pass

    def get_original_file(self) -> str:
        """
        Return the original file name.

        Returns:
            str: The name of the input file.
        """
        return self.file_name


class PDFInput(Input):
    """
    Concrete implementation of Input class for PDF files.
    """

    def __init__(self, file_name: str):
        """
        Initialize the PDFInput object with a file name and extract the text.

        Args:
            file_name (str): The name of the PDF file.
        """
        super().__init__(file_name)
        self.extracted_text = self._extract_text()

    def _extract_text(self) -> str:
        """
        Extract text from the PDF file.

        Returns:
            str: The extracted text from the PDF file.
        """
        try:
            with open(self.file_name, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    def get_text(self) -> str:
        """
        Return the extracted text from the PDF file.

        Returns:
            str: The extracted text from the PDF file.
        """
        return self.extracted_text
