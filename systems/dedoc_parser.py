from systems.base_parser import BasedParser

"""
    Documentation: https://github.com/ispras/dedoc
    1. Up docker-container: docker compose up --build
    2. pip install requests==2.32.3
"""


class DedocParser(BasedParser):

    def __init__(self):
        super().__init__()
        self.host = "0.0.0.0"
        self.port = "1231"
        self.data = {
            "document_type": "other",
            "return_format": "plain_text",
            "language": "rus+eng",
            "need_pdf_table_analysis": "false",
            "need_header_footer_analysis": "false",
            "is_one_column_document": "auto"
        }

    def parse(self, filename: str) -> str:
        import requests

        with open(filename, "rb") as file:
            files = {"file": (filename, file)}
            r = requests.post(f"http://{self.host}:{self.port}/upload", files=files, data=self.data)
            if r.status_code != 200:
                raise "dedoc's exception"

        text = r.content.decode()
        return text