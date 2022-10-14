from django.core.management import BaseCommand
from core.models import NtcRegionalOffice

from core.choices import ntc_region_choices


class Command(BaseCommand):
    """Create Initial Regional Office"""

    def handle(self, *args, **options):
        print("Creating NRO for superuser if not exists")
        for region_id, region_desc in ntc_region_choices:
            nro = NtcRegionalOffice.objects.filter(region=region_id)
            if not nro:
                print("No NRO found. Creating...")
                NtcRegionalOffice.objects.create(
                    region=region_id,
                    description=region_desc)
                print("Done!")
