import csv
import decimal


questions = {'Q1': ('Q1.tsv', 'Person', 'Total'), 'Q2': ('Q2.tsv', 'Student', 'Total')}
total_sheet = 'total.tsv'
total_sheet_person_col = 'Person'

question_data = {}
for k, v in questions.items():
    assert(k not in question_data)
    question_data[k] = {}
    question_file = v[0]
    person_col = v[1]
    total_col = v[2]
    with open(question_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            person = row[person_col]
            total = decimal.Decimal(row[total_col])
            assert(person not in question_data[k])
            question_data[k][person] = total

with open(total_sheet, 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        person = row[total_sheet_person_col]
        for k, v in question_data.items():
            total = decimal.Decimal(row[k])
            if total != question_data[k][person]:
                print('question: %s, person: %s' % (k, person))
                assert(False)


