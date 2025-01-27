"""Runs NLP on each study"""

import os
import re
from pathlib import Path

import ijson
import spacy

# from spacy import displacy
from spacy.matcher import DependencyMatcher
from tqdm import tqdm

from utils import get_project_root

# from dotenv import load_dotenv


base_path = get_project_root()

# load_dotenv()
# TERMS = os.getenv("TERMS")


def study_processor(folder_dir: Path = None):
    """Processes each study incrementally"""
    if folder_dir is None:
        items = os.listdir(base_path)
        responses = [item for item in items if item.startswith("responses")]

        def extract_key(item):
            match = re.search(r"\d+", item)
            return int(match.group()) if match else -1

        sorted_responses = sorted(responses, key=extract_key, reverse=True)
        folder_dir = base_path / str(sorted_responses[0])
        print(f"File path not selected, defaulting to: {folder_dir}")
    first_file = folder_dir / "query_result_0.json"
    with open(first_file, "rb") as f:
        count = ijson.items(f, "totalCount")
        try:
            total_count = int(next(count))
        except StopIteration:
            print("Total count not found. Only one page exist")
    with tqdm(total=total_count, desc="Processing Studies", unit="study") as p_bar:
        nlp, matcher = nlp_init()
        for file in folder_dir.iterdir():
            if file.is_file():
                with file.open("rb") as f:
                    parser = ijson.items(f, "studies.item")
                    for study in parser:
                        search_nlp(nlp, matcher, study)
                        # print(study["protocolSection"]["identificationModule"]["nctId"])
                        p_bar.update(1)


patterns = [
    {
        "label": "TNM_AJCC_Staging",
        "pattern": [
            {"RIGHT_ID": "tnm", "RIGHT_ATTRS": {"ORTH": "TNM"}},
            {
                "LEFT_ID": "tnm",
                "REL_OP": "<",
                "RIGHT_ID": "staging",
                "RIGHT_ATTRS": {"DEP": "compound"},
            },
        ],
    }
]


def nlp_init():
    """Set up NLP spacy"""
    spacy.require_gpu()
    nlp = spacy.load("en_core_web_trf")
    matcher = DependencyMatcher(nlp.vocab)
    for p in patterns:
        matcher.add(p["label"], [p["pattern"]])
    return nlp, matcher


def nlp_test(nlp, matcher):
    """Test NLP"""
    text = """
    Invasion of the chest wall increases the T staging in the Tumor, Node, Mestasis (TNM) classification system 
    of lung cancer to a T3 and is associated with decreased survival and more extensive operative procedures. 
    We use the AJCC staging system 7th edition.
    """
    doc = nlp(text)
    matches = matcher(doc)
    print("completed")
    print(matches)
    for match_id, start, end in matches:
        match_label = nlp.vocab.strings[match_id]
        matched_span = doc[start:end]
        print(f"Match found: {match_label}, Span: '{matched_span.text}'")


def search_nlp(nlp, matcher, study):
    """Runs NLP matching to find keywords"""
    doc = nlp(study)
    matches = matcher(doc)
    for match_id, start, end in matches:
        match_label = nlp.vocab.strings[match_id]
        matched_span = doc[start:end]
        print(f"Match found: {match_label}, Span: '{matched_span.text}'")
    # displacy.serve(matches)


nlp_c, matcher_c = nlp_init()
nlp_test(nlp_c, matcher_c)
