from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID

from datetime import datetime, timedelta
from random import SystemRandom
from .certdb import make_fields


def make_cert():
    """Generate and return a public key PEM and a secret key PEM."""
    secretkey = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    secretkey_pem = secretkey.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    f = make_fields()
    attrs = []
    if f.country:
        attrs.append(x509.NameAttribute(NameOID.COUNTRY_NAME, f.country))
    if f.state:
        attrs.append(x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, f.state))
    if f.locality:
        attrs.append(x509.NameAttribute(NameOID.LOCALITY_NAME, f.locality))
    if f.org:
        attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, f.org))
    if f.unit:
        attrs.append(x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, f.unit))
    if f.common:
        attrs.append(x509.NameAttribute(NameOID.COMMON_NAME, f.common))

    rng = SystemRandom()
    date_from = datetime.utcnow() - timedelta(
        days=f.delta * rng.randint(0, 80) / 100,
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
        seconds=rng.randint(0, 59),
    )
    dns_list = []
    for name in f.dns_names:
        dns_list.append(x509.DNSName(name))

    subject = issuer = x509.Name(attrs)
    cert = x509.CertificateBuilder() \
        .subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(secretkey.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(date_from) \
        .not_valid_after(date_from + timedelta(days=f.delta)) \
        .add_extension(x509.SubjectAlternativeName(dns_list), critical=False) \
        .sign(secretkey, hashes.SHA256(), default_backend())

    publickey_pem = cert.public_bytes(serialization.Encoding.PEM)

    return (publickey_pem, secretkey_pem)


def main():
    public, secret = make_cert()
    with open('public.pem', 'wb') as f:
        f.write(public)
        f.flush()
    with open('secret.pem', 'wb') as f:
        f.write(secret)
        f.flush()

if __name__ == '__main__':
    main()


__all__ = ['make_cert']
