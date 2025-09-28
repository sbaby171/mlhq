import json
import pymupdf4llm


def parse_pdf_to_md(pdf_path: str): 
    """Parse a PDF to markdown.

    Args: 
        pdf_path: Location on disk to the PDF file. 

    Returns:

    """
    return {
          "pdf_path": pdf_path, 
          "md_text": pymupdf4llm.to_markdown(pdf_path)
    } 


def get_function_by_name(name):
    if name == "parse_pdf_to_md":
        return parse_pdf_to_md

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "parse_pdf_to_md",
            "description": "Parse PDF to markdown",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {
                        "type": "string",
                        "description": 'Path on file to the PDF',
                    },
                },
                "required": ["pdf_path"],
            },
        },
    },
]
