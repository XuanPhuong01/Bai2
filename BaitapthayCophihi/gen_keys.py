from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
import os

# === CẤU HÌNH ĐƯỜNG DẪN LƯU FILE ===
BASE_DIR = r"E:\BaitapthayCophihi"
KEYS_DIR = os.path.join(BASE_DIR, "keys")
os.makedirs(KEYS_DIR, exist_ok=True)

PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "signer_key.pem")
CERT_PATH = os.path.join(KEYS_DIR, "signer_cert.pem")

# === 1. TẠO PRIVATE KEY RSA 2048 BIT ===
print("🔐 Đang tạo private key RSA 2048-bit...")
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# === 2. TẠO CERTIFICATE TỰ KÝ ===
print("📜 Đang tạo chứng chỉ tự ký (self-signed certificate)...")

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Thanh Hoa"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Thanh Hoa"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "K58KTPM"),
    x509.NameAttribute(NameOID.COMMON_NAME, "Nguyen Thi Xuan Phuong"),
])

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(private_key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow())
    .not_valid_after(datetime.utcnow() + timedelta(days=365))  # 1 năm
    .add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    )
    .sign(private_key, hashes.SHA256())
)

# === 3. GHI FILE PRIVATE KEY ===
with open(PRIVATE_KEY_PATH, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
print(f"✅ Đã lưu private key tại: {PRIVATE_KEY_PATH}")

# === 4. GHI FILE CERTIFICATE ===
with open(CERT_PATH, "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print(f"✅ Đã lưu certificate tại: {CERT_PATH}")

# === 5. HOÀN TẤT ===
print("\n🎉 Tạo cặp khóa & chứng chỉ tự ký thành công!")
