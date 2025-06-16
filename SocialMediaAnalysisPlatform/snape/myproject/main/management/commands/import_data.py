from django.core.management.base import BaseCommand
import pandas as pd
from main.models import Data  # Replace 'myapp' with your actual app name

class Command(BaseCommand):
    help = 'Populate the Data model from a CSV file'

    def handle(self, *args, **kwargs):
        # Load data from CSV
        df = pd.read_csv('export.csv')  # Ensure this path is correct

        # Populate the Data model
        for _, row in df.iterrows():
            Data.objects.create(
                name=row['name'],
                age=row['age'],
                from_location=row['from_location'],
                klout_score=row['klout_score']
            )

        self.stdout.write(self.style.SUCCESS('Data successfully populated.'))
