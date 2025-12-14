# CSCE411_ER_Diagram_Cardinality_Checker

## How to Run
Run the comparison script with text input and PlantUML input:

python actual_comparison.py text.txt diagram.puml

If no arguments are provided, the program runs using a built-in example.

## Expected Input
### Text Description (example):
A college offers many courses.
The same course is never taught by more than one instructor.

### PlantUML Diagram (example)
@startuml
entity College
entity Course
entity Instructor

College ||--o{ Course : offers
Instructor }o--|| Course : teaches
@enduml
## Expected Output
### The program prints:
Cardinality relationships extracted from the text

Relationships parsed from the PlantUML diagram

A comparison result for each relationship:

### Example:
Relationship: College -- offers --> Course

Status: match

Relationship: Instructor -- teaches --> Course

Status: match

### Possible statuses:
match — text and diagram agree

mismatch — cardinalities conflict

no_text_info — insufficient text data
