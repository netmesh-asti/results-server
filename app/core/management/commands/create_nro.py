from django.core.management import BaseCommand
from core.models import RegionalOffice

from core.choices import region_choices


class Command(BaseCommand):
    """Create Initial Regional Office"""

    def handle(self, *args, **options):
        print("Creating NRO for superuser if not exists")
        for region_id, region_desc in region_choices:
            nro = RegionalOffice.objects.filter(region=region_id)
            if not nro.exists():
                print("No NRO found. Creating...")
                RegionalOffice.objects.create(
                    region=region_id,
                    description=region_desc)
                print("Done!")
