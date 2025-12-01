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
from nltk.corpus import stopwords
import re

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
    nltk.download('punkt_tab')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')

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

RELATIONSHIP_VERBS = [
    'has', 'have', 'offers', 'offer', 'teach', 'teaches', 'taught',
    'contains', 'contain', 'includes', 'include', 'owns', 'own',
    'manages', 'manage', 'works', 'work', 'belongs', 'belong',
    'enrolls', 'enroll', 'takes', 'take', 'uses', 'use'
]

def extract_cardinality_sentences(text):
    sentences = sent_tokenize(text)
    cardinality_sentences = []
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in CARDINALITY_KEYWORDS.keys()):
            cardinality_sentences.append(sentence)
    
    return cardinality_sentences

def extract_entities_and_verbs(sentence):
    tokens = word_tokenize(sentence)
    pos_tags = nltk.pos_tag(tokens)
    
    entities = []
    verbs = []
    
    for word, tag in pos_tags:
        if tag.startswith('NN'):
            entities.append(word.lower())
        elif tag.startswith('VB'):
            verbs.append(word.lower())
    
    return entities, verbs

def identify_cardinality(sentence):
    sentence_lower = sentence.lower()
    found_cardinalities = []
    
    for keyword, cardinality in CARDINALITY_KEYWORDS.items():
        if keyword in sentence_lower:
            found_cardinalities.append((keyword, cardinality))
    
    return found_cardinalities

def extract_relationships(text):
    cardinality_sentences = extract_cardinality_sentences(text)
    relationships = []
    
    for sentence in cardinality_sentences:
        entities, verbs = extract_entities_and_verbs(sentence)
        cardinalities = identify_cardinality(sentence)
        
        relationship_verbs = [v for v in verbs if v in RELATIONSHIP_VERBS]
        
        if relationship_verbs and entities and cardinalities:
            relationships.append({
                'sentence': sentence,
                'entities': entities,
                'verbs': relationship_verbs,
                'cardinality_indicators': cardinalities
            })
    
    return relationships

text = """There are several colleges in the university. Each college has a name, location, and size. 
A college offers many courses. Course#, name, and credit hours describe a course. 
No two courses in any college have the same course#; likewise, no two courses have the same name. 
The college also has several instructors. Instructors teach; that is why they are called instructors. 
The same course is never taught by more than one instructor. Furthermore, instructors are capable of 
teaching a variety of courses offered by the college. Instructors have unique employee IDs, and their 
names, qualifications, and experience are also recorded."""

cardinality_sentences = extract_cardinality_sentences(text)

print("\n" + "=" * 80)
print("Cardinality Relationships:")
print("=" * 80)

relationships = extract_relationships(text)
for i, rel in enumerate(relationships, 1):
    print(f"\n{i}. Sentence: {rel['sentence']}")
    print(f"   Entities: {', '.join(set(rel['entities']))}")
    print(f"   Verbs: {', '.join(set(rel['verbs']))}")
    print(f"   Cardinality: {', '.join([f'{k} ({v})' for k, v in rel['cardinality_indicators']])}")