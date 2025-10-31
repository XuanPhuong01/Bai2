from datetime import datetime
from pyhanko.sign import signers, fields
from pyhanko.stamp.text import TextStampStyle
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.pdf_utils.layout import SimpleBoxLayoutRule, AxisAlignment, Margins
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec

# === CẤU HÌNH ĐƯỜNG DẪN ===
PDF_IN = r"E:\BaitapthayCophihi\bai2.pdf"
PDF_OUT = r"E:\BaitapthayCophihi\signed.pdf"
KEY_FILE = r"E:\BaitapthayCophihi\keys\signer_key.pem"
CERT_FILE = r"E:\BaitapthayCophihi\keys\signer_cert.pem"
SIG_IMG = r"E:\BaitapthayCophihi\assets\chuki.jpg"

print("🔹 Bước 1: Chuẩn bị PDF gốc (bai2.pdf - nội dung bài tập).")

# === TẠO SIGNER (KHÔNG TRUYỀN validation_context) ===
try:
    signer = signers.SimpleSigner.load(KEY_FILE, CERT_FILE, key_passphrase=None)
except Exception as e:
    print("❌ Lỗi khi tải khóa/chứng chỉ:", e)
    exit(1)

print("🔹 Bước 2: Chuẩn bị vùng ký (SigField1) & ảnh chữ ký...")

# === MỞ FILE PDF GỐC ===
with open(PDF_IN, "rb") as inf:
    writer = IncrementalPdfFileWriter(inf)

    # --- TẠO TRƯỜNG CHỮ KÝ ---
    sig_field_spec = SigFieldSpec(
        sig_field_name="SigField1",
        box=(240, 50, 550, 150),
        on_page=0
    )
    fields.append_signature_field(writer, sig_field_spec)

    # --- NỀN ẢNH CHỮ KÝ ---
    background_img = images.PdfImage(SIG_IMG)

    # Layout ảnh & chữ
    bg_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MIN,
        y_align=AxisAlignment.ALIGN_MID,
        margins=Margins(right=20)
    )
    text_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MIN,
        y_align=AxisAlignment.ALIGN_MID,
        margins=Margins(left=150)
    )

    text_style = TextBoxStyle(font_size=12)

    # --- NỘI DUNG CHỮ KÝ ---
    ngay_ky = datetime.now().strftime("%d/%m/%Y")
    stamp_text = (
        "Nguyen Thi Xuan Phuong"
        "\nSDT: 0966520806"
        "\nMSV: K225480106054"
        f"\nNgày ký: {ngay_ky}"
    )

    stamp_style = TextStampStyle(
        stamp_text=stamp_text,
        background=background_img,
        background_layout=bg_layout,
        inner_content_layout=text_layout,
        text_box_style=text_style,
        border_width=1,
        background_opacity=1.0,
    )

    print("🔹 Bước 3: Thiết lập metadata & thuật toán ký (SHA-256, RSA 2048-bit).")

    meta = signers.PdfSignatureMetadata(
        field_name="SigField1",
        reason="Nộp bài: Chữ ký số PDF - 58KTP",
        location="Thanh Hoa, Viet Nam",
        md_algorithm="sha256",
    )

    # --- KHÔNG TRUYỀN validation_context (sửa lỗi TypeError) ---
    pdf_signer = signers.PdfSigner(
        signature_meta=meta,
        signer=signer,
        stamp_style=stamp_style,
    )

    print("🔹 Bước 4-7: Thực hiện ký và ghi incremental update...")

    try:
        with open(PDF_OUT, "wb") as outf:
            pdf_signer.sign_pdf(writer, output=outf)
        print("✅ Ký thành công! File đã lưu tại:", PDF_OUT)
    except Exception as e:
        print("❌ Lỗi khi ký PDF:", e)
        exit(1)

print("🎉 Hoàn tất quá trình ký PDF.")
