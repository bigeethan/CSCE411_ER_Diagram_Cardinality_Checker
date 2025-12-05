import re

# Map PlantUML ER cardinality symbols to semantic names
PLANTUML_CARDINALITY_MAP = {
    '||': 'one',
    '|o': 'zero_or_one',
    'o|': 'zero_or_one',
    '}o': 'zero_or_many',
    'o{': 'zero_or_many',
    '}|': 'one_or_many',
    '|{': 'one_or_many',
    '': None,  # no explicit cardinality
}

# Regex to match lines like:
#   College ||--o{ Course : offers
#   Instructor }o--|| Course : teaches
REL_PATTERN = re.compile(
    r"""
    ^\s*
    (?P<left_entity>[A-Za-z_][A-Za-z0-9_]*)        # left entity name
    \s+
    (?P<left_card>[|}{o]{0,2})                     # left cardinality symbols (optional)
    [-.]+                                          # -- or .. or similar
    (?P<right_card>[|}{o]{0,2})                    # right cardinality symbols (optional)
    \s+
    (?P<right_entity>[A-Za-z_][A-Za-z0-9_]*)       # right entity name
    (?:\s*:\s*(?P<label>.+))?                      # optional label after colon
    $
    """,
    re.VERBOSE
)

def normalize_plantuml_cardinality(symbols: str):
    """Map PlantUML symbol pairs like '||' or 'o{' to a semantic label."""
    return PLANTUML_CARDINALITY_MAP.get(symbols, None)

def parse_plantuml_relationships(plantuml_text: str):
    """
    Parse PlantUML ER relationships from text and return a list of dicts:
    {
        'left_entity': 'College',
        'right_entity': 'Course',
        'left_cardinality': 'one',
        'right_cardinality': 'zero_or_many',
        'raw_left': '||',
        'raw_right': 'o{',
        'label': 'offers',
        'label_verb': 'offers'
    }
    """
    relationships = []

    for line in plantuml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("'"):  # skip empty/comment lines
            continue

        m = REL_PATTERN.match(line)
        if not m:
            continue

        left_entity = m.group('left_entity')
        right_entity = m.group('right_entity')
        left_card_raw = m.group('left_card') or ''
        right_card_raw = m.group('right_card') or ''
        label = (m.group('label') or '').strip()

        left_card_norm = normalize_plantuml_cardinality(left_card_raw)
        right_card_norm = normalize_plantuml_cardinality(right_card_raw)

        # crude guess: first word of label is the verb, if any
        label_verb = label.split()[0].lower() if label else None

        relationships.append({
            'left_entity': left_entity,
            'right_entity': right_entity,
            'left_cardinality': left_card_norm,
            'right_cardinality': right_card_norm,
            'raw_left': left_card_raw,
            'raw_right': right_card_raw,
            'label': label,
            'label_verb': label_verb,
        })

    return relationships