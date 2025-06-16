import csv
from main.models import Data

# Path to your CSV file
csv_file_path = "data.csv"

# Read and load data
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        Data.objects.create(
            name=row['name'],
            age=row['age'] if row['age'] else None,
            from_location=row['from_location'],
            klout_score=row['klout_score'] if row['klout_score'] else None,
        )

print("Data successfully loaded!")
