"""Main Pipeline"""

from nlp import nlp_init, nlp_match
from transformer import transformer_init
from utils import get_project_root, json_to_xlsx, study_processor
import time


def secondary_filter(study):
    """Filter after getting responses"""
    if "protocolSection" not in study:
        return None
    
    match_json = []
    all_editions = set()

    def determine_edition(matches):
        editions = set()
        has_sub_8th = False
        
        for match in matches:
            label = next(k for k in match if k not in ["sentence", "edition"])
            if label in ["T_STAGE_SUB", "M_STAGE_SUB"]:
                editions.add("7th")
                editions.add("8th")
            elif label in ["T_STAGE_SUB_8TH", "M_STAGE_SUB_8TH"]:
                has_sub_8th = True
            elif label == "NUM_EDITION" or label == "LETTER_EDITION":
                edition_text = match[label].lower()
                if "sixth" in edition_text or "6th" in edition_text:
                    editions.add("6th")
                elif "seventh" in edition_text or "7th" in edition_text:
                    editions.add("7th")
                elif "eighth" in edition_text or "8th" in edition_text:
                    editions.add("8th")
        
        if has_sub_8th:
            return ["8th"]  # definitive
        elif editions:
            return list(editions)  # editions found
        else:
            return ["6th", "7th", "8th"]  # all possible

    if "descriptionModule" in study["protocolSection"]:
        if "briefSummary" in study["protocolSection"]["descriptionModule"]:
            # print("Checking desc")
            text = study["protocolSection"]["descriptionModule"]["briefSummary"]
            text_doc = nlp(text)
            matches = nlp_match(nlp, matcher, text_doc)
            if matches:
                match_json.extend(matches)
                editions = determine_edition(matches)
                all_editions.update(editions)
                for m in matches:
                    if "edition" not in m:
                        m["possible_editions"] = editions
            #     result = classifier(text, labels, multi_label=True)
            #     if result:
            #         temp_dict = {"matcher": matches, "classifier": result}
            #         match_json.append(temp_dict)
            #     else:
            #         print("No result from transformer")
    if "outcomesModule" in study["protocolSection"]:
        # print("Checking outcomes")
        for k, v in study["protocolSection"]["outcomesModule"].items():
            for i in v:
                if "description" in i:
                    text = i["description"]
                    text_doc = nlp(text)
                    matches = nlp_match(nlp, matcher, text_doc)
                    if matches:
                        match_json.extend(matches)
                        editions = determine_edition(matches)
                        all_editions.update(editions)
                        for m in matches:
                            if "edition" not in m:
                                m["possible_editions"] = editions
                    # if matches:
                    #     result = classifier(text, labels, multi_label=True)
                    #     if result:
                    #         temp_dict = {"matcher": matches, "classifier": result}
                    #         match_json.append(temp_dict)
                    #     else:
                    #         print("No result from transformer")
    if not match_json:
        return None
    
    study_editions = list(all_editions) if all_editions else ["6th", "7th", "8th"]
    return {"matches": match_json, "possible_editions": study_editions}


if __name__ == "__main__":
    nlp, matcher = nlp_init()
    classifier, labels = transformer_init()
    json_path = study_processor(secondary_filter)
    root_dir = get_project_root()
    save_file = root_dir / f"{int(round(time.time()))}_output.xlsx"
    json_to_xlsx(json_path, save_file)
