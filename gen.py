from OpenSSL import crypto

# Generate a private key
private_key = crypto.PKey()
private_key.generate_key(crypto.TYPE_RSA, 2048)

# Generate a certificate request
cert_request = crypto.X509Req()
cert_request.get_subject().CN = "www.miubackend.net"
cert_request.set_pubkey(private_key)
cert_request.sign(private_key, "sha256")
cert_request.add_extensions([crypto.X509Extension(b"subjectAltName", False, b"DNS:www.miubackend.net")])

# Generate a self-signed certificate
certificate = crypto.X509()
certificate.gmtime_adj_notBefore(0)
certificate.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for one year
certificate.set_issuer(cert_request.get_subject())
certificate.set_subject(cert_request.get_subject())
certificate.set_pubkey(cert_request.get_pubkey())
certificate.sign(private_key, "sha256")

# Save the private key and certificate to files
with open("key.pem", "wb") as key_file:
    key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))

with open("cert.pem", "wb") as cert_file:
    cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
