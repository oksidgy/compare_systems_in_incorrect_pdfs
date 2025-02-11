import time
import os
import json
from typing import Dict, List
import re
import zipfile

import wget

from metric import calculate_accuracy_script


def download_dataset(data_dir: str) -> str:
    benchmark_data_dir = os.path.join(data_dir, "data_for_dedoc_benchmarks")
    if not os.path.isdir(benchmark_data_dir):
        path_out = os.path.join(data_dir, "data_for_dedoc_benchmarks.zip")
        wget.download("https://at.ispras.ru/owncloud/index.php/s/IvVzvoqZsj5PMpM/download", path_out)
        with zipfile.ZipFile(path_out, "r") as zip_ref:
            zip_ref.extractall(data_dir)
        os.remove(path_out)
        print(f"Benchmark data downloaded to {benchmark_data_dir}")
    else:
        print(f"Use cached benchmark data from {benchmark_data_dir}")

    assert os.path.isdir(benchmark_data_dir)

    return benchmark_data_dir


def _init_statistics_by_system() -> Dict:
    return {"Accuracy": [], "Status": [], "Time": [], "Filename": []}


def _update_statistic_by_system(statistic: Dict, accuracy_path: str, status: str, time_predict: float, filename: str) -> Dict:
    with open(accuracy_path, "r") as f:
        lines = f.readlines()
        matched = [line for line in lines if "Accuracy After Correction" in line]
        if not matched:
            matched = [line for line in lines if "Accuracy\n" in line]
        acc_percent = re.findall(r"-*\d+\.\d+", matched[0])[0][:-1]
        statistic["Accuracy"].append(float(acc_percent))
        print(statistic["Accuracy"][-1])
        statistic["Status"].append(status)
        statistic["Time"].append(time_predict)
        statistic["Filename"].append(filename)

    return statistic


def _get_avg(array: List) -> float:
    return sum(array) / len(array) if array else 0.0


def _calculate_statistic(statistic: Dict) -> Dict:
    accs, times, failed_cnt, failed_filenames = [], [], 0, []
    for ind, element in enumerate(statistic["Status"]):
        if not element == "failed":
            acc = 0. if float(statistic["Accuracy"][ind]) < 0 else float(statistic["Accuracy"][ind])
            accs.append(acc)
            times.append(statistic["Time"][ind])
        else:
            failed_cnt += 1
            failed_filenames.append(statistic["Filename"][ind])

    statistic["AVG_Time"] = _get_avg(times)
    statistic["AVG_Accuracy"] = _get_avg(accs)
    statistic["Failed count"] = failed_cnt
    statistic["Failed docs"] = failed_filenames

    return statistic


def run_system(system_name: str, base_path: str) -> None:

    # Initialization paths
    parser_path = os.path.join(base_path, f"runs/{system_name}")
    os.makedirs(parser_path, exist_ok=True)
    dir_accuracy = os.path.join(parser_path, "accuracy")
    os.makedirs(dir_accuracy, exist_ok=True)
    dir_predict = os.path.join(parser_path, "predict")
    os.makedirs(dir_predict, exist_ok=True)

    benchmark_data_dir = download_dataset(base_path)
    dataset_path = os.path.join(benchmark_data_dir, "incorrect/pdf")
    dataset_gt_path = os.path.join(benchmark_data_dir, "incorrect/txt")

    # Initialization step
    statistic = _init_statistics_by_system()

    if system_name == "docling":
        from systems.docling_parser import DoclingParser
        parser = DoclingParser()
    if system_name == "unstructured":
        from systems.unstructured_parser import UnstructuredParser
        parser = UnstructuredParser()
    if system_name == "dedoc":
        from systems.dedoc_parser import DedocParser
        parser = DedocParser()

    for filename in os.listdir(dataset_path):
        if not os.path.isfile(os.path.join(dataset_path, filename)):
            continue
        print(f"Handle {filename}")
        basename = filename.split(".")[0]
        status = "success"

        # Prediction step
        time_b = time.time()
        try:
            text = parser.parse(os.path.join(dataset_path, filename))
        except Exception as ex:
            print(ex)
            text = ""
            status = "failed"
        time_predict = time.time() - time_b

        # Save prediction
        path_predict = os.path.join(dir_predict, basename + ".txt")
        if os.path.exists(path_predict):
            os.remove(path_predict)
        with open(path_predict, "w") as f_predict:
            f_predict.write(text)

        # Calculate character accuracy
        accuracy_path = os.path.join(dir_accuracy, f"{basename}_accuracy.txt")
        if os.path.exists(accuracy_path):
            os.remove(accuracy_path)

        gt_path = os.path.join(dataset_gt_path, f"{basename}.txt")
        calculate_accuracy_script(gt_path, path_predict, accuracy_path)

        # Update information
        statistic = _update_statistic_by_system(statistic, accuracy_path, status, time_predict, filename)

    statistic = _calculate_statistic(statistic)
    with open(f'benchmark_incorrect_{system_name}.json', 'w') as f_res:
        json.dump(statistic, f_res, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    intermediate_data_path = os.path.join(os.path.expanduser("~"), ".cache", "dedoc", "resources")
    base_dir = os.path.join(intermediate_data_path, "benchmark_incorrect_pdf_diff_systems")
    os.makedirs(base_dir, exist_ok=True)

    # run_system(system_name="docling", base_path=base_dir)
    run_system(system_name="unstructured", base_path=base_dir)
    # run_system(system_name="dedoc", base_path=base_dir)