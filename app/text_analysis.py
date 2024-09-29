
import spacy
import textstat
import detectlanguage

import os
nlp = spacy.load("pl_core_news_sm")

def calculate_readability(text):
    # Calculate readability scores
    flesch_score = textstat.flesch_reading_ease(text)
    gunning_fog_score = textstat.gunning_fog(text)

    return flesch_score, gunning_fog_score


def detect_language_errors(text):
    doc = nlp(text)
    errors = []

    # Check for long sentences
    for sent in doc.sents:
        if len(sent) > 20:  # Example criterion: more than 20 words
            errors.append("Long sentence: {}".format(sent.text))

    # Check for jargon or complex words
    complex_words = ['efektywny', 'przedsiębiorstwo']  # Example complex words
    for token in doc:
        if token.text in complex_words:
            errors.append("Jargon detected: {}".format(token.text))

    return errors

def analyze_text(text):
    flesch, gunning_fog = calculate_readability(text)
    language_errors = detect_language_errors(text)
    return {
        "flesch": flesch,
        "gunning": gunning_fog,
        "errors": language_errors,
        "foreign_language": detect_foreign_language(text),
        "use_passive_voice": is_passive_voice(text),
    }

def compare_phonetic_text(text1, text2):
    doc1 = nlp(text1)
    doc2 = nlp(text2)

    # Calculate similarity between the two documents
    similarity = doc1.similarity(doc2)
    return similarity

def detect_foreign_language(transcription):
    detectlanguage.configuration.api_key = "313199b8e970410d3643d15635192e5f"


    languages = detectlanguage.detect(transcription)
    polish_detected = any(lang['language'] == 'pl' for lang in languages)
    foreign_words_flag = any(lang['language'] != 'pl' and lang["isReliable"] == True for lang in languages)

    return {"is_polish": polish_detected, "foreign_words": foreign_words_flag}

def is_passive_voice(sentence):
    doc = nlp(sentence)
    for token in doc:
        # Check for passive voice based on the presence of auxiliary verb "być" and a past participle
        if token.dep_ == 'aux' and token.lemma_ == 'być':
            # Look for the verb that follows "być" and check if it's a past participle
            next_token = token.nbor()
            if next_token.tag_ in ['VBD', 'VBN']:  # VBD = past tense verb, VBN = past participle
                return True

    return False
