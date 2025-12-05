'''
Step 1: Gather keywords based on ER descriptions
Step 2: Assign those keywords with specific cardinality
Step 3: Find a way to read an actual diagram
Step 4: Find a way to read through a description to find keywords
Step 5: Get an expected cardinality from the description
Step 6: Get the actual cardinality from the diagram
Step 7: Compare the two
'''

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer

# -----------------------------------------------------------------------------
# NLTK setup
# -----------------------------------------------------------------------------
# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Some NLTK installs use punkt_tab; if missing, download it
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except:
        # not all NLTK versions have this; ignore if missing
        pass

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# -----------------------------------------------------------------------------
# Keyword configuration
# -----------------------------------------------------------------------------
CARDINALITY_KEYWORDS = {
    'many': 'many',
    'several': 'many',
    'multiple': 'many',
    'variety': 'many',
    'each': 'one',
    'one': 'one',
    'single': 'one',
    'a': 'one',
    'an': 'one',
    'unique': 'one',
    'same': 'one',
    'never': 'constraint',
}

# IMPORTANT: use base forms (lemmas) here
RELATIONSHIP_VERBS = [
    'have',
    'offer',
    'teach',
    'contain',
    'include',
    'own',
    'manage',
    'work',
    'belong',
    'enroll',
    'take',
    'use',
    'employ',
]

# -----------------------------------------------------------------------------
# Text-side extraction
# -----------------------------------------------------------------------------
def extract_cardinality_sentences(text: str):
    sentences = sent_tokenize(text)
    cardinality_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in CARDINALITY_KEYWORDS.keys()):
            cardinality_sentences.append(sentence)
    
    return cardinality_sentences


def extract_entities_and_verbs(sentence: str):
    """
    Extract nouns (entities), verb surface forms, and verb lemmas
    from a sentence. Only verbs whose lemma is in RELATIONSHIP_VERBS
    are kept.
    """
    tokens = word_tokenize(sentence)
    pos_tags = nltk.pos_tag(tokens)
    
    entities = []
    verbs = []         # original verb tokens, e.g., "offers", "taught"
    verb_lemmas = []   # normalized forms, e.g., "offer", "teach"
    
    for word, tag in pos_tags:
        w = word.lower()
        if tag.startswith('NN'):
            entities.append(w)
        elif tag.startswith('VB'):
            lemma = lemmatizer.lemmatize(w, 'v')
            if lemma in RELATIONSHIP_VERBS:
                verbs.append(w)
                verb_lemmas.append(lemma)
    
    return entities, verbs, verb_lemmas


def identify_cardinality(sentence: str):
    sentence_lower = sentence.lower()
    found_cardinalities = []
    
    for keyword, cardinality in CARDINALITY_KEYWORDS.items():
        if keyword in sentence_lower:
            found_cardinalities.append((keyword, cardinality))
    
    return found_cardinalities


def extract_relationships(text: str):
    """
    Return a list of relationship dicts:
    {
        'sentence': ...,
        'entities': [...],
        'verbs': [...],         # surface verb forms
        'verb_lemmas': [...],   # normalized base forms
        'cardinality_indicators': [(keyword, kind), ...]
    }
    """
    cardinality_sentences = extract_cardinality_sentences(text)
    relationships = []
    
    for sentence in cardinality_sentences:
        entities, verbs, verb_lemmas = extract_entities_and_verbs(sentence)
        cardinalities = identify_cardinality(sentence)
        
        if verb_lemmas and entities and cardinalities:
            relationships.append({
                'sentence': sentence,
                'entities': entities,
                'verbs': verbs,
                'verb_lemmas': verb_lemmas,
                'cardinality_indicators': cardinalities
            })
    
    return relationships


def summarize_text_cardinality(relationships_from_text):
    """
    For each verb lemma, aggregate cardinality indicators from the text.
    Returns:
      lemma -> {'one': count, 'many': count, 'constraint': count}
    """
    summary = {}

    for rel in relationships_from_text:
        for lemma in rel.get('verb_lemmas', []):
            if lemma not in summary:
                summary[lemma] = {'one': 0, 'many': 0, 'constraint': 0}

            for _, card in rel['cardinality_indicators']:
                if card in summary[lemma]:
                    summary[lemma][card] += 1

    return summary