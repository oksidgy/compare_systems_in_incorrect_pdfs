import os

"""
    Calculation accuracy build for Ubuntu from source https://github.com/eddieantonio/ocreval
"""


def calculate_accuracy_script(tmp_gt_path: str, tmp_prediction_path: str, accuracy_path: str) -> None:
    accuracy_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "accuracy"))
    command = f"{accuracy_script_path} {tmp_gt_path} {tmp_prediction_path} >> {accuracy_path}"
    os.system(command)