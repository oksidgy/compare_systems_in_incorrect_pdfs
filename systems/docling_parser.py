from systems.base_parser import BasedParser

"""
    Documentation: https://github.com/DS4SD/docling
    pip install docling==2.15.1
"""


class DoclingParser(BasedParser):

    def __init__(self):
        super().__init__()
        from docling.document_converter import DocumentConverter
        self.parser = DocumentConverter()

    def parse(self, filename: str) -> str:
        result = self.parser.convert(filename)
        return "\n".join([blob.text for blob in result.document.texts])
