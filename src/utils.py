"""Utilities"""

import glob
import json
import os
import time
from datetime import datetime
from pathlib import Path

import ijson
import pandas as pd
import pytz
from tqdm import tqdm


def get_project_root() -> Path:
    """Return project root"""
    return Path(__file__).parent.parent


def get_latest_response_dir() -> Path:
    """Return Latest Response Path"""
    base_path = get_project_root()
    pattern = os.path.join(base_path, "responses_*")
    responses = glob.glob(pattern)
    responses = [Path(x) for x in responses]

    responses.sort(key=lambda x: int(x.name.split("_")[-1]), reverse=True)

    if responses:
        return responses[0]
    return None


def study_processor(exec_func, folder_dir: Path = None):
    """Processes each study incrementally"""
    if folder_dir is None:
        folder_dir = get_latest_response_dir()
        if folder_dir is not None:
            print(f"File path not selected, defaulting to: {folder_dir}")
        else:
            print("No responses found")
            return
    first_file = folder_dir / "query_result_0.json"
    with open(first_file, "rb") as f:
        count = ijson.items(f, "totalCount")
        try:
            total_count = int(next(count))
        except StopIteration:
            print("Total count not found")
            return
    project_root = get_project_root()
    save_dir = project_root / f"processed_{int(round(time.time()))}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_path = save_dir / "processed_studies.json"
    if os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            processed_json = json.load(f)
    else:
        processed_json = []
    with tqdm(total=total_count, desc="Processing Studies", unit="study") as p_bar:
        for file in folder_dir.iterdir():
            if file.is_file():
                with file.open("rb") as f:
                    parser = ijson.items(f, "studies.item")
                    for study in parser:
                        result = exec_func(study)
                        if result:
                            save_result = {
                                "nctId": study["protocolSection"]["identificationModule"]["nctId"],
                                "startDate": study["protocolSection"]["statusModule"]["startDateStruct"]["date"],
                                "possible_editions": result["possible_editions"],
                                "matches": result["matches"],
                            }
                            processed_json.append(save_result)
                        # else:
                        # print("No result from exec_func")
                        p_bar.update(1)
    print(f"Saving Json to {save_path}")
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(processed_json, f, indent=4)
    return save_path


def json_to_xlsx(file_path, save_path):
    with open(file_path, "r", encoding="utf-8") as f:
        json_file = json.load(f)
    df = pd.DataFrame(json_file)
    df.to_excel(save_path, index=False, engine="openpyxl")


def epoch_to_datetime(epoch, timezone="Europe/London"):
    """Epoch to Datetime in UK timezone"""
    timezone = pytz.timezone(timezone)
    return (
        datetime.fromtimestamp(epoch).astimezone(timezone).strftime("%Y-%m-%d %H:%M:%S")
    )


def datetime_to_epoch(dt, timezone="Europe/London"):
    """Datetime to Epoch in UK timezone"""
    timezone = pytz.timezone(timezone)
    dtime = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    dtime = timezone.localize(dtime.replace(tzinfo=None))
    return int(dtime.timestamp())
