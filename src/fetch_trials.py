"""Manages all requests and responses to ClinicalTrials.gov"""

import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import httpx
import ijson
from dotenv import load_dotenv
from tqdm import tqdm

from utils import get_project_root

load_dotenv()
API_URL = os.getenv("API_URL")
QUERY = os.getenv("QUERY")
Q_FILTER = os.getenv("Q_FILTER")
base_path = get_project_root()


def params_creator(
    query: str, q_filter: str, page_token: str = None, page_size: int = 100
):
    """Parses a dictionary for params"""
    if page_token is None:
        return {
            "filter.advanced": query,
            "postFilter.advanced": q_filter,
            "countTotal": True,
            "pageSize": page_size,
        }
    return {
        "filter.advanced": query,
        "postFilter.advanced": q_filter,
        "countTotal": True,
        "pageSize": page_size,
        "pageToken": page_token,
    }


def fetch_studies(params: dict):
    """Fetch all studies according to query"""
    dir_name = f"responses_{int(round(time.time()))}"
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    save_dir = base_path / dir_name
    with httpx.Client() as client:
        save_name = "query_result_0"
        save_path = save_dir / f"{save_name}.json"
        get_studies(client, params, save_path)
        nextpage = True
        pagecounter = 0
        while nextpage:
            with open(save_path, "rb") as f:
                try:
                    nextpagetoken = next(ijson.items(f, "nextPageToken"))
                    params = params_creator(QUERY, Q_FILTER, nextpagetoken)
                    pagecounter += 1
                    save_name = save_name.split("_")
                    save_name[2] = str(pagecounter)
                    save_name = "_".join(save_name)
                    save_path = save_dir / f"{save_name}.json"
                    get_studies(client, params, save_path)
                except StopIteration:
                    print("All pages have been parsed")
                    nextpage = False


def get_studies(client: httpx.Client, params: dict, save_path: Path):
    """Get studies response from ClinicalTrials.gov API"""
    url = urljoin(API_URL, "studies")
    elapsed = time.time()
    with client.stream("GET", url, params=params) as response:
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    print("Response saved;" f" Elapsed {(time.time() - elapsed)* 1000} milliseconds")


def get_study_by_id(client: httpx.Client, nctid: str, save_path: Path):
    """Get study response by nctId"""
    url = urljoin(API_URL, "studies")
    url = urljoin(url, nctid)
    elapsed = time.time()
    with client.stream("GET", url) as response:
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    print("Response saved;" f" Elapsed {(time.time() - elapsed)* 1000} milliseconds")


if __name__ == "__main__":
    q_params = params_creator(QUERY, Q_FILTER)
    fetch_studies(q_params)
