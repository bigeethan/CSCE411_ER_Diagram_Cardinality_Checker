'''
Step 1: Gather keywords based on ER descriptions
Step 2: Assign those keywords with specific cardinality
Step 3: Find a way to read an actual diagram
Step 4: Find a way to read through a description to find keywords
Step 5: Get an expected cardinality from the description
Step 6: Get the actual cardinality from the diagram
Step 7: Compare the two
'''

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except:
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

CARDINALITY_KEYWORDS = {
    # ONE/SINGLE
    'one': 'one',
    'single': 'one',
    'a': 'one',
    'an': 'one',
    'each': 'one',
    'every': 'one',
    'individual': 'one',
    'unique': 'one',
    'only one': 'one',
    'exactly one': 'one',
    'one and only': 'one',
    'same': 'one',
    'specific': 'one',
    'particular': 'one',
    'sole': 'one',
    
    # MANY
    'many': 'many',
    'multiple': 'many',
    'several': 'many',
    'various': 'many',
    'variety': 'many',
    'numerous': 'many',
    'different': 'many',
    'any number': 'many',
    'zero or more': 'many',
    'one or more': 'many',
    'more than one': 'many',
    'unlimited': 'many',
    'diverse': 'many',
    'range': 'many',
    'collection': 'many',
    'set': 'many',
    'list': 'many',
    'group': 'many',
    
    # OPTIONAL
    'optional': 'optional',
    'may': 'optional',
    'might': 'optional',
    'can': 'optional',
    'could': 'optional',
    'optionally': 'optional',
    'zero or one': 'optional',
    'at most one': 'optional',
    
    # MANDATORY
    'must': 'mandatory',
    'required': 'mandatory',
    'always': 'mandatory',
    'necessary': 'mandatory',
    'need': 'mandatory',
    'shall': 'mandatory',
    'should': 'mandatory',
    'has to': 'mandatory',
    
    # CONSTRAINT
    'never': 'constraint',
    'cannot': 'constraint',
    'not': 'constraint',
    'no': 'constraint',
    'without': 'constraint',
    'except': 'constraint',
    'exclude': 'constraint',
    
    # EXACT
    'exactly': 'exact',
    'precisely': 'exact',
    'at least': 'minimum',
    'minimum': 'minimum',
    'at most': 'maximum',
    'maximum': 'maximum',
    'up to': 'maximum',
}

def extract_cardinality_sentences(text: str):
    """Extract sentences that contain cardinality keywords."""
    sentences = sent_tokenize(text)
    cardinality_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in CARDINALITY_KEYWORDS.keys()):
            cardinality_sentences.append(sentence)
    
    return cardinality_sentences

def extract_entities_and_verbs(sentence: str):
    """
    Extract ALL nouns (entities) and ALL verbs from a sentence.
    No filtering - works with any domain.
    """
    tokens = word_tokenize(sentence)
    pos_tags = nltk.pos_tag(tokens)
    
    entities = []
    verbs = []         # original verb tokens
    verb_lemmas = []   # normalized forms
    
    for word, tag in pos_tags:
        w = word.lower()
        if tag.startswith('NN'):
            entities.append(w)
        elif tag.startswith('VB'):
            lemma = lemmatizer.lemmatize(w, 'v')
            verbs.append(w)
            verb_lemmas.append(lemma)
    
    return entities, verbs, verb_lemmas

def identify_cardinality(sentence: str):
    """Identify all cardinality indicators in a sentence."""
    sentence_lower = sentence.lower()
    found_cardinalities = []
    
    # Sort keywords by length (longest first) to match multi-word phrases first
    sorted_keywords = sorted(CARDINALITY_KEYWORDS.items(), key=lambda x: len(x[0]), reverse=True)
    
    for keyword, cardinality in sorted_keywords:
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
    Works with ANY ER diagram description - no domain-specific filtering.
    """
    cardinality_sentences = extract_cardinality_sentences(text)
    relationships = []
    
    for sentence in cardinality_sentences:
        entities, verbs, verb_lemmas = extract_entities_and_verbs(sentence)
        cardinalities = identify_cardinality(sentence)
        
        # Include relationships even if no verbs found (some relationships use prepositions)
        if entities and cardinalities:
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
    If no verbs, use '__preposition__' as key for prepositional relationships.
    Returns:
      lemma -> {'one': count, 'many': count, 'optional': count, 'mandatory': count, ...}
    """
    summary = {}
    cardinality_types = ['one', 'many', 'optional', 'mandatory', 'constraint', 'exact', 'minimum', 'maximum']

    for rel in relationships_from_text:
        lemmas = rel.get('verb_lemmas', [])
        
        # If no verbs found, use a generic key
        if not lemmas:
            lemmas = ['__preposition__']
        
        for lemma in lemmas:
            if lemma not in summary:
                summary[lemma] = {card_type: 0 for card_type in cardinality_types}

            for _, card in rel['cardinality_indicators']:
                if card in summary[lemma]:
                    summary[lemma][card] += 1

    return summary