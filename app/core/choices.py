import pytz

registration_choices = [
        ('registered', 'Registered'),
        ('unregistered', 'Unregistered'),
        ('disabled', 'Disabled')
    ]

ntc_region_choices = [
    ('1', 'Region I (Ilocos Region)'),
    ('2', 'Region II (Cagayan Valley)'),
    ('3', 'Region III (Central Luzon)'),
    ('4-A', 'Region IV-A (CALABARZON)'),
    ('4-B', 'Region IV-B MIMAROPA Region'),
    ('5', 'Region V (Bicol Region)'),
    ('6', 'Region VI (Western Visayas)'),
    ('7', 'Region VII (Central Visayas)'),
    ('8',  'Region VIII (Eastern Visayas)'),
    ('9', 'Region IX (Zamboanga Peninsula)'),
    ('10', 'Region X (Northern Mindanao)'),
    ('11', 'Region XI (Davao Region)'),
    ('12', 'Region XII (SOCCSKSARGEN)'),
    ('13',  'Region XIII (Caraga)'),
    ('NCR', 'National Capital Region (NCR)'),
    ('CAR', 'Cordillera Administrative Region (CAR)'),
    ('BARMM', 'Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)'),
    ('Central', 'NTC Region Central'),
    ('unknown', 'Unknown'),
    ('Demo', 'Demo')
]

device_choices = [
        ('unknown', 'Unknown'),
        ('computer', 'Computer'),
        ('smartphone', 'Smart Phone'),
        ('tablet', 'Tablet')
    ]

network_choices = [
    ('unkown', 'unknown'),
    ('2g', '2G'),
    ('3g', '3G'),
    ('4g', '4G'),
    ('lte', 'LTE'),
    ('dsl', 'DSL'),
]

server_choices = [
    ('local', 'Local'),
    ('overseas', 'Overseas'),
    ('ix', 'Internet Exchange'),
    ('web-based', 'Web-based'),
    ('rfc', 'RFC 6349'),
    ('unknown', 'Unknown')
]

test_type_choices = [
    ('0', 'unknown'),
    ('1', 'other'),
    ('2', 'RFC 6349'),
    ('3', 'Web-based'),
]

timezone_choices = [(v, v) for v in pytz.common_timezones]

direction_choices = [
    ('forward', 'Forward'),  # client to test server
    ('reverse', 'Reverse'),  # test server to client
    ('unknown', 'Unknown')
]

test_mode_choices = [
    ('upload', 'Upload Mode'),      # formerly normal mode
    ('download', 'Download Mode'),  # formerly reverse mode
    ('bidirectional', 'bidirectional'),  # formerly reverse mode
    ('simultaneous', 'Simultaneous Mode'),
    ('unknown', 'Unknown')
]
