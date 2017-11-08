from collections import namedtuple
from random import SystemRandom

Fields = namedtuple('Fields', ['country', 'state', 'locality', 'org', 'unit', 'common', 'delta', 'dns_names'])

def make_fields():
    rng = SystemRandom()

    field_id = rng.randint(-len(default_fields), len(default_fields) - 1)
    if field_id >= 0:
        return default_fields[field_id]

    country = rng.choice(list_country)
    state = rng.choice(list_state)
    locality = rng.choice(list_locality)
    org = ''
    unit = ''

    org_cond = rng.randint(0, 3)
    if org_cond == 1:
        org = rng.choice(list_org)
    elif org_cond == 2:
        unit = rng.choice(list_org)
    elif org_cond == 3:
        org = rng.choice(list_org)
        unit = rng.choice(list_org)

    common = rng.choice(list_common)
    delta = rng.choice(list_delta)

    dns_set = set()
    dns_count = max(0, rng.randint(-7, 7))
    for i in range(dns_count):
        dns_set.add(rng.choice(list_dns))
    if (not dns_set) or rng.randint(0, 5):
        dns_set.add('localhost')
    dns_names = sorted(dns_set)

    return Fields(
        country=country,
        state=state,
        locality=locality,
        org=org,
        unit=unit,
        common=common,
        delta=delta,
        dns_names=dns_names,
    )

##############################################################################

pyca_docs = Fields(
    country='US',
    state='CA',
    locality='San Francisco',
    org='My Company',
    unit='',
    common='mysite.com',
    delta=10,
    dns_names=['localhost'],
)

python_docs = Fields(
    country='US',
    state='MyState',
    locality='Some City',
    org='My Organization, Inc.',
    unit='My Group',
    common='myserver.mygroup.myorganization.com',
    delta=30,
    dns_names=['localhost'],
)

openssl_1 = Fields(
    country='AU',
    state='Some-State',
    locality='',
    org='Internet Widgits Pty Ltd',
    unit='',
    common='',
    delta=30,
    dns_names=['localhost'],
)

openssl_2 = Fields(
    country='GB',
    state='Berkshire',
    locality='Newbury',
    org='My Company Ltd',
    unit='',
    common='',
    delta=30,
    dns_names=['localhost'],
)

zeronet_default = Fields(
    country='US',
    state='NY',
    locality='New York',
    org='Example, LLC',
    unit='',
    common='Example Company',
    delta=30,
    dns_names=['example.com', 'www.example.com', 'mail.example.com', 'ftp.example.com'],
)

localhost_1 = Fields(
    country='',
    state='',
    locality='',
    org='',
    unit='',
    common='localhost',
    delta=30,
    dns_names=['localhost'],
)

localhost_2 = Fields(
    country='',
    state='',
    locality='',
    org='',
    unit='',
    common='',
    delta=30,
    dns_names=['localhost'],
)

default_fields = (
    pyca_docs, python_docs,
    openssl_1, openssl_2, zeronet_default, localhost_1, localhost_2,
)


list_country = [
    'US', 'CA', 'JP', 'AU', 'GB', 'CH', 'GR',
    'HU', 'IE', 'IT', 'FI', 'FR', 'DE', 'CR', 'CZ', 'DK', 'TR', 'NO', 'PE',
    'NZ', 'MX', 'RO', 'ES', 'RU', 'PL', 'PT', 'PR',
]

list_state = [
    'Berkshire',
    'Bern',
    'Greece',
    'Some-State', 'State', 'Province', 'State or Province Name', 'localhost',
    '',

    'AL', 'Alabama', 'AK', 'Alaska', 'AZ', 'Arizona', 'AR', 'Arkansas',
    'CA', 'California', 'CO', 'Colorado', 'CT', 'Connecticut', 'DE', 'Delaware',
    'FL', 'Florida', 'GA', 'Georgia', 'HI', 'Hawaii', 'ID', 'Idaho',
    'IL', 'Illinois', 'IN', 'Indiana', 'IA', 'Iowa', 'KS', 'Kansas',
    'KY', 'Kentucky', 'LA', 'Louisiana', 'ME', 'Maine', 'MD', 'Maryland',
    'MA', 'Massachusetts', 'MI', 'Michigan', 'MN', 'Minnesota',
    'MS', 'Mississippi', 'MO', 'Missouri', 'MT', 'Montana', 'NE', 'Nebraska',
    'NV', 'Nevada', 'NH', 'New Hampshire', 'NJ', 'New Jersey',
    'NM', 'New Mexico', 'NY', 'New York', 'NC', 'North Carolina',
    'ND', 'North Dakota', 'OH', 'Ohio', 'OK', 'Oklahoma', 'OR', 'Oregon',
    'PA', 'Pennsylvania', 'RI', 'Rhode Island', 'SC', 'South Carolina',
    'SD', 'South Dakota', 'TN', 'Tennessee', 'TX', 'Texas', 'UT', 'Utah',
    'VT', 'Vermont', 'VA', 'Virginia', 'WA', 'Washington',
    'WV', 'West Virginia', 'WI', 'Wisconsin', 'WY', 'Wyoming',
    'PR', 'Puerto Rico',

    'Ontario', 'ON', 'Quebec', 'QC', 'Nova Scotia', 'NS', 'New Brunswick', 'NB',
    'Manitoba', 'MB', 'British Columbia', 'BC', 'Prince Edward Island', 'PE',
    'Saskatchewan', 'SK', 'Alberta', 'AB', 'Newfoundland and Labrador', 'NL',
]

list_locality = [
    'Newbury',
    'Oberdiessbach',
    'Thessaloniki',
    'Montreal',
    'Tokyo', 'Kyoto',
    'Locality Name', 'Locality', 'City', 'localhost', 'local',
    '',

    'San Francisco', 'Mountain View', 'Los Angeles', 'Hawthorne',
    'New York', 'New York City', 'NYC', 'Chicago', 'New Orleans',
    'Portland', 'Baltimore', 'Detroit', 'Minneapolis', 'Kansas City',
    'Las Vagas', 'Manchester', 'Charlotte', 'Albuquerque', 'Fargo',
    'Philadelphia', 'Charleston', 'Sioux Falls', 'Houston', 'Burlington',
    'Virginia Beach', 'Seattle', 'Milwaukee',

    'Montgomery', 'Juneau', 'Phoenix', 'Little Rock', 'Sacramento', 'Denver',
    'Hartford', 'Dover', 'Tallahassee', 'Atlanta', 'Honolulu', 'Boise',
    'Springfield', 'Indianapolis', 'Des Moines', 'Topeka', 'Frankfort',
    'Baton Rouge', 'Augusta', 'Annapolis', 'Boston', 'Lansing', 'Saint Paul',
    'Jackson', 'Jefferson City', 'Helena', 'Lincoln', 'Carson City', 'Concord',
    'Trenton', 'Santa Fe', 'Albany', 'Raleigh', 'Bismarck', 'Columbus',
    'Oklahoma City', 'Salem', 'Harrisburg', 'Providence', 'Columbia', 'Pierre',
    'Nashville', 'Austin', 'Salt Lake City', 'Montpelier', 'Richmond',
    'Olympia', 'Charleston', 'Madison', 'Cheyenne',

    'Toronto', 'Montreal', 'Halifax', 'Fredericton', 'Moncton', 'Winnipeg',
    'Victoria', 'Vancouver', 'Charlottetown', 'Regina', 'Saskatoon', 'Edmonton',
    'Calgary', 'St. John\'s',

    'Nagoya', 'Toyohashi', 'Okazaki', 'Ichinomiya', 'Seto', 'Handa', 'Kasugai',
    'Toyokawa', 'Tsushima', 'Hekinan', 'Toyota', 'Anjo', 'Nishio', 'Inuyama',
    'Tokoname', 'Konan', 'Komaki', 'Inazawa', 'Tokai', 'Obu', 'Chita', 'Chiryu',
    'Owariasahi', 'Takahama', 'Iwakura', 'Toyoake', 'Nisshin', 'Tahara', 'Aisai',
    'Kiyosu', 'Shinshiro', 'Yatomi', 'Miyoshi', 'Nagakute', 'Akita', 'Odate',
    'Kazuno', 'Daisen', 'Katagami', 'Kitaakita', 'Oga', 'Yurihonjo', 'Yuzawa',
    'Semboku', 'Yokote', 'Nikaho', 'Noshiro', 'Hachinohe', 'Kuroishi', 'Misawa',
    'Mutsu', 'Towada', 'Tsugaru', 'Goshogawara', 'Aomori', 'Hirakawa',
    'Hirosaki', 'Chiba', 'Choshi', 'Ichikawa', 'Funabashi', 'Tateyama',
    'Kisarazu', 'Matsudo', 'Noda', 'Mobara', 'Narita', 'Sakura', 'Togane',
    'Narashino', 'Kashiwa', 'Katsuura', 'Ichihara', 'Nagareyama', 'Yachiyo',
    'Abiko', 'Kamagaya', 'Kimitsu', 'Futtsu', 'Urayasu', 'Yotsukaido',
    'Sodegaura', 'Yachimata', 'Inzai', 'Shiroi', 'Tomisato', 'Kamogawa',
    'Asahi', 'Isumi', 'Sosa', 'Minamiboso', 'Katori', 'Sanmu', 'Oamishirasato',
    'Matsuyama', 'Niihama',
]

list_org = [
    'Internet Widgits Pty Ltd', 'World Wide Web Pty Ltd',
    'My Company', 'My Company Ltd', 'Company', 'Company Name', 'My Group',
    'My Organization, Inc.', 'My Organization Inc', 'My Organization',
    'My Network', 'My Server', 'My Web Server',
    'My Certificate Authority', 'Root CA', 'CA Root',
    'Certification Authority',
    'Example, LLC', 'optional', 'web', 'Web',
    'ABCDEF Corporation',
    'Organization Name', 'Organization',
    'Domain Control Validated',

    'my', 'My', 'MY', 'my test', 'PC', 'pc', 'my pc',
    'localhost', 'home', 'my home', 'My Home', 'work', 'workgroup',
    'test', 'TEST', 'Test', 'Test Company', 'Test Company Ltd',
    'IT', 'IT GROUP', 'IT TEAM', 'IT Group', 'IT Team', 'IT Department',
    'Information Security Department', 'Information Department', 'Information Group',
    '',
]

list_common = [
    'Example Company', 'IT', 'CA', 'Certification Authority',
    'TempCA', 'CN=TempCA', 'CN = TempCA',
    'SignedByCA', 'CN=SignedByCA', 'CN = SignedByCA',
    'Common', 'Common Name', 'Root CA', 'Trusted Root Certification Authorities',
    'CertSign', 'Root',
    'mysite.com', 'www.mysite.com', '*.mysite.com',
    'example.com', 'www.example.com', '*.example.com',
    'example.org',  'www.example.org', '*.example.org',
    'server', 'Server', 'Host-01', 'localhost', '127.0.0.1', '192.168.1.1',
    'example', 'whatever', 'demoCA', 'demo', 'test', 'work', 'workgroup',
    '',
]

list_delta = [
    10, 15, 28, 29, 30, 31, 60, 90, 100, 120,
    360, 365, 365*2, 365*3, 3600, 3650,
]

list_dns = [
    'localhost.localdomain', 'localhost.invalid', 'invalid.invalid', 'invalid.localdomain',
    'server', 'nas', 'pi', 'router', 'wifi', 'wlan', 'whatever', 'example', 'demo', 'test', 'work', 'workgroup',
    'mysite.com', 'www.mysite.com',
    'mydomain.com', 'www.mydomain.com', 'site1.mydomain.com',
    'example.com', 'www.example.com', 'mail.example.com', 'server.example.com',
    'ftp.example.com',
    'example.org', 'www.example.org', 'mail.example.org', 'server.example.org',
    'ftp.example.org',
]
