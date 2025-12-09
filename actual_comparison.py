'''
Generalized ER Diagram Comparison Tool
Compares text descriptions with PlantUML diagrams for ANY domain
'''
from cardinality_checker import extract_relationships, summarize_text_cardinality, lemmatizer
from plantUML_checker import parse_plantuml_relationships

import sys

def compare_text_and_plantuml(text_relationships, plantuml_relationships):
    """
    Compare the cardinality hints in the text vs the PlantUML diagram.
    """
    text_summary = summarize_text_cardinality(text_relationships)
    results = []

    for prel in plantuml_relationships:
        verb = prel['label_verb']
        if not verb:
            results.append({
                'plantuml_rel': prel,
                'status': 'no_text_info',
                'details': 'Relationship has no label verb; skipping text comparison.'
            })
            continue

        # Normalize PlantUML label verb to lemma
        v = verb.lower()
        lemma = lemmatizer.lemmatize(v, 'v')

        verb_info = text_summary.get(lemma)
        if not verb_info:
            results.append({
                'plantuml_rel': prel,
                'status': 'no_text_info',
                'details': f'No cardinality keywords in text for verb lemma "{lemma}".'
            })
            continue

        plantuml_cards = {prel['left_cardinality'], prel['right_cardinality']}
        plantuml_cards.discard(None)

        expected = set()
        if verb_info['many'] > 0:
            expected.add('many')
        if verb_info['one'] > 0:
            expected.add('one')

        many_like = {'one_or_many', 'zero_or_many'}
        one_like = {'one', 'zero_or_one'}

        ok = True
        explanation_parts = []
        if 'many' in expected:
            if not plantuml_cards & many_like:
                ok = False
                explanation_parts.append(
                    "Text suggests 'many', but diagram has no many-side cardinality."
                )
        if 'one' in expected:
            if not plantuml_cards & one_like:
                ok = False
                explanation_parts.append(
                    "Text suggests 'one', but diagram has no one-side cardinality."
                )

        if ok:
            status = 'match'
            if not explanation_parts:
                explanation_parts.append(
                    "Text and diagram cardinalities look consistent."
                )
        else:
            status = 'mismatch'

        details = " ".join(explanation_parts) + f" (text summary: {verb_info}, diagram: {plantuml_cards})"

        results.append({
            'plantuml_rel': prel,
            'status': status,
            'details': details
        })

    return results


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        # Read from command line arguments or files
        arg1, arg2 = sys.argv[1], sys.argv[2]
        
        # Check if arguments are file paths
        try:
            with open(arg1, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            text = arg1  # Treat as direct text input
        
        try:
            with open(arg2, 'r', encoding='utf-8') as f:
                plantuml = f.read()
        except FileNotFoundError:
            plantuml = arg2  # Treat as direct PlantUML input
        
        print("=" * 80)
        print("Using custom input from command line arguments")
        print("=" * 80)
    else:
        # Default example
        print("=" * 80)
        print("Using default example (University domain)")
        print("To use your own: python actual_comparison.py text.txt diagram.puml")
        print("=" * 80)
        
        text = """There are several colleges in the university. Each college has a name, location, and size. 
        A college offers many courses. Course#, name, and credit hours describe a course. 
        No two courses in any college have the same course#; likewise, no two courses have the same name. 
        The college also has several instructors. Instructors teach; that is why they are called instructors. 
        The same course is never taught by more than one instructor. Furthermore, instructors are capable of 
        teaching a variety of courses offered by the college. Instructors have unique employee IDs, and their 
        names, qualifications, and experience are also recorded."""

        plantuml = """
        @startuml
        entity College
        entity Course
        entity Instructor

        College ||--o{ Course : offers
        College ||--o{ Instructor : employs
        Instructor }o--|| Course : teaches
        @enduml
        """

    print("\n" + "=" * 80)
    print("Cardinality Relationships from TEXT:")
    print("=" * 80)

    text_relationships = extract_relationships(text)
    for i, rel in enumerate(text_relationships, 1):
        print(f"\n{i}. Sentence: {rel['sentence']}")
        print(f"   Entities: {', '.join(set(rel['entities']))}")
        print(f"   Verbs: {', '.join(set(rel['verbs']))}")
        print(f"   Cardinality: {', '.join([f'{k} ({v})' for k, v in rel['cardinality_indicators']])}")

    print("\n" + "=" * 80)
    print("Relationships from PlantUML:")
    print("=" * 80)

    plantuml_relationships = parse_plantuml_relationships(plantuml)
    for i, prel in enumerate(plantuml_relationships, 1):
        print(f"\n{i}. {prel['left_entity']} {prel['raw_left']}--{prel['raw_right']} {prel['right_entity']} : {prel['label']}")
        print(f"   Left cardinality:  {prel['left_cardinality']}")
        print(f"   Right cardinality: {prel['right_cardinality']}")

    print("\n" + "=" * 80)
    print("Comparison (Text vs PlantUML):")
    print("=" * 80)

    comparison_results = compare_text_and_plantuml(text_relationships, plantuml_relationships)
    for i, res in enumerate(comparison_results, 1):
        prel = res['plantuml_rel']
        print(f"\n{i}. Relationship: {prel['left_entity']} -- {prel['label']} --> {prel['right_entity']}")
        print(f"   Status:  {res['status']}")
        print(f"   Details: {res['details']}")