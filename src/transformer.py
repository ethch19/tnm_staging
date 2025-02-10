""" NLP with BERT """

from transformers import pipeline

extracts = [
    "Percentage of participants with tumor stages 0, 1, 2, 3 and 4, as per Tumor, Node, Metastasis (TNM) staging system, during anytime between initial BC disease diagnosis and index date were reported in this outcome measure. As per TNM staging system, tumor stage 0 indicates main tumor cannot be found; tumor stages 1, 2, 3 and 4 refers to the size and/or extent of the main tumor. The higher the number, the larger the tumor and/or the more it has spread into nearby tissues. Data for this outcome measure is also presented by de novo status.",
    "Compare the cancer stage (IASCL 9th edition TNM-classification) as determined by FAPI PET/CT compared to conventional imaging (including FDG PET/CT) at primary staging.",
    "Patients affected by locally advanced non-small-cell lung cancer (staged III according to 8th TNM classification), undergoing induction therapy (IT) followed by either radical surgery or immunotherapy boost and treated in Fondazione Policlinico Universitario A. Gemelli IRCCS of Rome, Italy, will be enrolled in this study.",
]

labels = [
    "AJCC",
    "UICC",
    "IASLC",
    "6th edition",
    "7th edition",
    "8th edition",
    "9th edition",
]


def transformer_init():
    """Init Transformer"""
    return (
        pipeline(
            "zero-shot-classification",
            model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
            device="cuda",
        ),
        labels,
    )
    # output = classifier(text, labels, multi_label=True)
