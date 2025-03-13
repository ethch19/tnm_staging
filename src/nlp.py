"""Runs NLP on each study"""

import spacy
from spacy.matcher import Matcher

patterns = [
    {
        "label": "T_STAGE",
        "pattern": [{"TEXT": {"regex": r"^[Tt][0-4]$"}}],
    },
    {
        "label": "N_STAGE", # ALL editions
        "pattern": [{"TEXT": {"regex": r"^[Nn][0-3]$"}}],
    },
    {
        "label": "m_STAGE",
        "pattern": [{"TEXT": {"regex": r"^[Mm][0-1]$"}}],
    },
    {
        "label": "T_STAGE_SUB", # >7th
        "pattern": [{"TEXT": {"REGEX": r"^[Tt][1-2][ab]$"}}],
    },
    {
        "label": "T_STAGE_SUB_8TH", # 8th only
        "pattern": [{"TEXT": {"REGEX": r"^[Tt]1c$"}}],
    },
    {
        "label": "M_STAGE_SUB", # >7th
        "pattern": [{"TEXT": {"REGEX": r"^[Mm]1[ab]$"}}],
    },
    {
        "label": "M_STAGE_SUB_8TH", # 8th only
        "pattern": [{"TEXT": {"REGEX": r"^[Mm]1c$"}}],
    },
    {
        "label": "NUM_EDITION",
        "pattern": [
            {"LIKE_NUM": True },
            {"lower": { "IN": ["edition", "ed.", "ed"] }},
        ],
    },
    {
        "label": "TNM_CLASSIFICATION",
        "pattern": [
            {"LOWER": "tnm"},
            {"OP": "?"},
            {"LOWER": {"FUZZY": "classification"}},
        ],
    },
    {
        "label": "TNM_STAGING",
        "pattern": [
            {"LOWER": "tnm"},
            {"OP": "?"},
            {"LOWER": "staging"},
        ],
    },
    {
        "label": "TNM_LONG",
        "pattern": [
            {"LOWER": {"FUZZY": "tumour"}},
            {"OP": "?", "IS_PUNCT": True},
            {"LOWER": "node"},
            {"OP": "?", "IS_PUNCT": True},
            {"LOWER": {"FUZZY": "metastasis"}},
        ],
    },
]
# numerical words

def nlp_init():
    """Set up NLP spacy"""
    spacy.require_gpu()
    nlp = spacy.load("en_core_web_trf")
    matcher = Matcher(nlp.vocab)
    for p in patterns:
        matcher.add(p["label"], [p["pattern"]])
    return nlp, matcher


def nlp_match(nlp, matcher, text):
    """Runs NLP matching to find keywords"""
    doc = nlp(text)
    matches = matcher(doc)
    if matches:
        matches_list = []
        for match_id, start, end in matches:
            temp_dict = {}
            match_label = nlp.vocab.strings[match_id]
            matched_span = doc[start:end]
            temp_dict[str(match_label)] = str(matched_span.text)
            for sent in doc.sents:
                if sent.start <= start and sent.end >= end:
                    temp_dict["sentence"] = str(sent.text)
                    break
            matches_list.append(temp_dict)
            # print(f"Match found: {match_label}, Span: '{matched_span.text}'")
        return matches_list
    else:
        return None


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


if __name__ == "__main__":
    nlp, matcher = nlp_init()
    nlp_test(nlp, matcher)
