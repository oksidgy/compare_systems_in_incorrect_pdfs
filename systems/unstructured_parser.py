from systems.base_parser import BasedParser

"""
    Documentation: https://pypi.org/project/unstructured/
    pip install unstructured==0.16.15
"""


class UnstructuredParser(BasedParser):

    def __init__(self):
        super().__init__()

    def parse(self, filename: str) -> str:
        from unstructured.partition.auto import partition
        result = partition(filename=filename)
        return "\n".join([blob.text for blob in result])