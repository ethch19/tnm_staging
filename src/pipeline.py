"""Main Pipeline"""

from nlp import nlp_init, nlp_match
from transformer import transformer_init
from utils import get_project_root, json_to_xlsx, study_processor


def secondary_filter(study):
    """Filter after getting responses"""
    if "protocolSection" in study:
        match_json = []
        if "descriptionModule" in study["protocolSection"]:
            if "briefSummary" in study["protocolSection"]["descriptionModule"]:
                # print("Checking desc")
                text = study["protocolSection"]["descriptionModule"]["briefSummary"]
                text_doc = nlp(text)
                matches = nlp_match(nlp, matcher, text_doc)
                if matches:
                    result = classifier(text, labels, multi_label=True)
                    if result:
                        temp_dict = {"matcher": matches, "classifier": result}
                        match_json.append(temp_dict)
                    else:
                        print("No result from transformer")
        if "outcomesModule" in study["protocolSection"]:
            # print("Checking outcomes")
            for k, v in study["protocolSection"]["outcomesModule"].items():
                for i in v:
                    if "description" in i:
                        text = i["description"]
                        text_doc = nlp(text)
                        matches = nlp_match(nlp, matcher, text_doc)
                        if matches:
                            result = classifier(text, labels, multi_label=True)
                            if result:
                                temp_dict = {"matcher": matches, "classifier": result}
                                match_json.append(temp_dict)
                            else:
                                print("No result from transformer")
        return match_json


if __name__ == "__main__":
    nlp, matcher = nlp_init()
    classifier, labels = transformer_init()
    json_path = study_processor(secondary_filter)
    root_dir = get_project_root()
    save_file = root_dir / "output.xlsx"
    json_to_xlsx(json_path, save_file)
