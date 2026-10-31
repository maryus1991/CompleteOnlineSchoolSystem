import csv
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

from django.db import transaction

from apps.categories.models import GradeCategories, MajorCategories
from apps.users.accounts.models import User
from apps.users.students.models import Student


STUDENT_TEMPLATE_COLUMNS = [
    ("phone_number", "شماره موبایل (الزامی)"),
    ("first_name", "نام (الزامی)"),
    ("last_name", "نام خانوادگی (الزامی)"),
    ("gender", "جنسیت (M/F یا مذکر/مونث)"),
    ("private_code", "کد ملی / کد اختصاصی"),
    ("parent_phone_number", "شماره والدین"),
    ("grade", "پایه تحصیلی"),
    ("major", "رشته تحصیلی"),
    ("province", "استان"),
    ("city", "شهر"),
    ("target_major_rank", "هدف تحصیلی"),
    ("password", "رمز عبور (اختیاری)"),
]

HEADER_ALIASES = {
    "phone_number": "phone_number",
    "phonenumber": "phone_number",
    "phone": "phone_number",
    "mobile": "phone_number",
    "شماره موبایل": "phone_number",
    "شماره موبایل (الزامی)": "phone_number",
    "شماره تلفن": "phone_number",
    "شماره": "phone_number",
    "موبایل": "phone_number",
    "first_name": "first_name",
    "firstname": "first_name",
    "نام": "first_name",
    "نام (الزامی)": "first_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "نام خانوادگی": "last_name",
    "نام خانوادگی (الزامی)": "last_name",
    "gender": "gender",
    "جنسیت": "gender",
    "جنسیت (m/f یا مذکر/مونث)": "gender",
    "private_code": "private_code",
    "national_code": "private_code",
    "کد ملی": "private_code",
    "کد ملی / کد اختصاصی": "private_code",
    "کد مخفی": "private_code",
    "parent_phone_number": "parent_phone_number",
    "parent_phone": "parent_phone_number",
    "شماره والدین": "parent_phone_number",
    "grade": "grade",
    "پایه": "grade",
    "پایه تحصیلی": "grade",
    "major": "major",
    "رشته": "major",
    "رشته تحصیلی": "major",
    "province": "province",
    "استان": "province",
    "city": "city",
    "شهر": "city",
    "target_major_rank": "target_major_rank",
    "هدف تحصیلی": "target_major_rank",
    "password": "password",
    "رمز عبور": "password",
    "رمز عبور (اختیاری)": "password",
}

PERSIAN_DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(val: str) -> str:
    if val is None:
        return ""
    return str(val).translate(PERSIAN_DIGIT_MAP).strip()


def normalize_iran_phone(raw_phone: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", normalize_digits(raw_phone))
    if cleaned.startswith("0098"):
        cleaned = "+98" + cleaned[4:]
    elif cleaned.startswith("98") and len(cleaned) == 12:
        cleaned = "+98" + cleaned[2:]
    elif cleaned.startswith("09") and len(cleaned) == 11:
        cleaned = "+98" + cleaned[1:]
    elif cleaned.startswith("9") and len(cleaned) == 10:
        cleaned = "+98" + cleaned
    return cleaned


def is_valid_iran_phone(phone: str) -> bool:
    return bool(re.match(r"^\+989\d{9}$", phone))


def _col_letter(idx_zero_based: int) -> str:
    result = ""
    n = idx_zero_based + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def build_xlsx_bytes(headers: list[str], rows: list[list], sheet_name: str = "Report") -> bytes:
    """
    ساخت فایل استاندارد اکسل (.xlsx) به صورت باینری در حافظه (بدون وابستگی خارجی)
    با پشتیبانی از راست‌به‌چپ (RTL) و کاراکترهای فارسی.
    """
    all_rows = [headers] + list(rows)
    sheet_rows_xml = []
    for r_idx, row_values in enumerate(all_rows, start=1):
        cells_xml = []
        for c_idx, val in enumerate(row_values):
            col_ref = f"{_col_letter(c_idx)}{r_idx}"
            if val is None:
                val_str = ""
            else:
                val_str = str(val)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                cells_xml.append(f'<c r="{col_ref}" t="n"><v>{val}</v></c>')
            else:
                escaped = xml_escape(val_str)
                cells_xml.append(
                    f'<c r="{col_ref}" t="inlineStr"><is><t xml:space="preserve">{escaped}</t></is></c>'
                )
        sheet_rows_xml.append(f'<row r="{r_idx}">{"".join(cells_xml)}</row>')

    worksheet_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetViews><sheetView rightToLeft="1" workbookViewId="0"/></sheetViews>'
        f'<sheetData>{"".join(sheet_rows_xml)}</sheetData>'
        '</worksheet>'
    )

    safe_sheet = xml_escape((sheet_name or "Sheet1")[:31])
    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets><sheet name="{safe_sheet}" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )

    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    wb_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", worksheet_xml)
    return buf.getvalue()


def build_csv_bytes(headers: list[str], rows: list[list]) -> bytes:
    sio = io.StringIO()
    writer = csv.writer(sio)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(["" if v is None else str(v) for v in row])
    return ("\ufeff" + sio.getvalue()).encode("utf-8")


def get_student_import_template_bytes(fmt: str = "xlsx") -> tuple[bytes, str, str]:
    headers = [col[0] for col in STUDENT_TEMPLATE_COLUMNS]
    sample_rows = [
        [
            "09121112233",
            "علی",
            "محمدی",
            "M",
            "0011223344",
            "09123334455",
            "دوازدهم",
            "تجربی",
            "تهران",
            "تهران",
            "پزشکی تهران",
            "Student@1234",
        ],
        [
            "09124445566",
            "سارا",
            "احمدی",
            "F",
            "0099887766",
            "09127778899",
            "یازدهم",
            "ریاضی",
            "اصفهان",
            "اصفهان",
            "مهندسی کامپیوتر",
            "Student@1234",
        ],
    ]
    if fmt == "csv":
        return (
            build_csv_bytes(headers, sample_rows),
            "text/csv; charset=utf-8",
            "students_import_template.csv",
        )
    return (
        build_xlsx_bytes(headers, sample_rows, sheet_name="StudentsTemplate"),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "students_import_template.xlsx",
    )


def _col_ref_to_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha()).upper()
    idx = 0
    for ch in letters:
        idx = idx * 26 + (ord(ch) - 64)
    return max(0, idx - 1)


def _read_xlsx_rows(raw_bytes: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(raw_bytes), "r") as zf:
        shared_strings = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in ss_root.iter():
                if si.tag.endswith("}si") or si.tag == "si":
                    texts = [
                        t.text or ""
                        for t in si.iter()
                        if t.tag.endswith("}t") or t.tag == "t"
                    ]
                    shared_strings.append("".join(texts))

        sheet_files = sorted(
            name
            for name in zf.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )
        if not sheet_files:
            raise ValueError("هیچ شیتی در فایل اکسل یافت نشد.")

        sheet_root = ET.fromstring(zf.read(sheet_files[0]))
        rows_out = []
        for row_el in sheet_root.iter():
            if not (row_el.tag.endswith("}row") or row_el.tag == "row"):
                continue
            row_cells = {}
            max_col = -1
            for c_el in row_el:
                if not (c_el.tag.endswith("}c") or c_el.tag == "c"):
                    continue
                ref = c_el.attrib.get("r", "")
                c_type = c_el.attrib.get("t", "")
                col_idx = _col_ref_to_index(ref) if ref else (max_col + 1)
                max_col = max(max_col, col_idx)
                val_text = ""
                if c_type == "inlineStr":
                    texts = [
                        t.text or ""
                        for t in c_el.iter()
                        if t.tag.endswith("}t") or t.tag == "t"
                    ]
                    val_text = "".join(texts)
                else:
                    v_el = next(
                        (
                            ch
                            for ch in c_el
                            if ch.tag.endswith("}v") or ch.tag == "v"
                        ),
                        None,
                    )
                    if v_el is not None and v_el.text is not None:
                        if c_type == "s":
                            s_idx = int(v_el.text)
                            val_text = (
                                shared_strings[s_idx]
                                if 0 <= s_idx < len(shared_strings)
                                else ""
                            )
                        else:
                            val_text = v_el.text
                row_cells[col_idx] = val_text.strip()
            if max_col >= 0:
                rows_out.append([row_cells.get(i, "") for i in range(max_col + 1)])
        return rows_out


def _read_csv_rows(raw_bytes: bytes) -> list[list[str]]:
    text = raw_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    return [[cell.strip() for cell in row] for row in reader if any(c.strip() for c in row)]


def parse_spreadsheet_upload(uploaded_file) -> tuple[list[str], list[dict]]:
    filename = (getattr(uploaded_file, "name", "") or "").lower()
    raw_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    if filename.endswith(".xlsx") or raw_bytes[:2] == b"PK":
        raw_rows = _read_xlsx_rows(raw_bytes)
    elif filename.endswith(".csv"):
        raw_rows = _read_csv_rows(raw_bytes)
    else:
        raise ValueError("فرمت فایل باید .xlsx یا .csv باشد.")

    if not raw_rows:
        raise ValueError("فایل بارگذاری‌شده خالی است.")

    raw_headers = [normalize_digits(h).strip() for h in raw_rows[0]]
    canonical_headers = []
    for h in raw_headers:
        key = HEADER_ALIASES.get(h.lower(), HEADER_ALIASES.get(h, h.lower()))
        canonical_headers.append(key)

    parsed_rows = []
    for idx, r in enumerate(raw_rows[1:], start=2):
        if not any(str(c).strip() for c in r):
            continue
        row_dict = {"_row_number": idx}
        for c_idx, col_key in enumerate(canonical_headers):
            row_dict[col_key] = r[c_idx].strip() if c_idx < len(r) else ""
        parsed_rows.append(row_dict)

    return canonical_headers, parsed_rows


def validate_and_import_students(
    uploaded_file,
    school,
    default_adviser=None,
) -> dict:
    """
    اعتبارسنجی دقیق ستون‌ها، نوع داده، یکتایی شماره موبایل و کد ملی
    و ثبت دسته‌جمعی اتمیک دانش‌آموزان برای مدرسه مربوط به مدیر.
    """
    try:
        headers, rows = parse_spreadsheet_upload(uploaded_file)
    except Exception as exc:
        return {
            "success": False,
            "created_count": 0,
            "total_rows": 0,
            "errors": [
                {
                    "row": 1,
                    "phone": "-",
                    "name": "ساختار فایل",
                    "messages": [str(exc)],
                }
            ],
            "created_students": [],
        }

    required_cols = {"phone_number", "first_name", "last_name"}
    missing_cols = required_cols - set(headers)
    if missing_cols:
        missing_str = "، ".join(sorted(missing_cols))
        return {
            "success": False,
            "created_count": 0,
            "total_rows": len(rows),
            "errors": [
                {
                    "row": 1,
                    "phone": "-",
                    "name": "ستون‌های الزامی",
                    "messages": [
                        f"ستون‌های الزامی زیر در فایل یافت نشدند: {missing_str}"
                    ],
                }
            ],
            "created_students": [],
        }

    if not rows:
        return {
            "success": False,
            "created_count": 0,
            "total_rows": 0,
            "errors": [
                {
                    "row": 2,
                    "phone": "-",
                    "name": "بدون داده",
                    "messages": ["هیچ ردیف دانش‌آموزی در فایل یافت نشد."],
                }
            ],
            "created_students": [],
        }

    grades_by_name = {
        g.name.strip(): g for g in GradeCategories.objects.filter(is_active=True)
    }
    majors_by_name = {
        m.name.strip(): m for m in MajorCategories.objects.filter(is_active=True)
    }

    existing_phones = set(
        str(p).replace(" ", "")
        for p in User.objects.values_list("PhoneNumber", flat=True)
    )
    existing_private_codes = set(
        c.strip()
        for c in User.objects.exclude(private_code__isnull=True)
        .exclude(private_code="")
        .values_list("private_code", flat=True)
    )

    seen_phones_in_file = {}
    seen_codes_in_file = {}
    row_errors = []
    prepared_records = []

    for row in rows:
        row_num = row["_row_number"]
        raw_phone = row.get("phone_number", "")
        phone = normalize_iran_phone(raw_phone)
        first_name = (row.get("first_name") or "").strip()
        last_name = (row.get("last_name") or "").strip()
        full_name = f"{first_name} {last_name}".strip() or "-"
        private_code = normalize_digits(row.get("private_code", "")).strip()
        parent_phone_raw = row.get("parent_phone_number", "")
        parent_phone = normalize_iran_phone(parent_phone_raw) if parent_phone_raw else ""
        gender_raw = (row.get("gender") or "M").strip().upper()
        grade_name = (row.get("grade") or "").strip()
        major_name = (row.get("major") or "").strip()
        province = (row.get("province") or school.province or "").strip()
        city = (row.get("city") or school.city or "").strip()
        target_major_rank = (row.get("target_major_rank") or "").strip()
        password = (row.get("password") or "").strip() or (private_code or phone[-8:])

        msgs = []
        if not first_name:
            msgs.append("نام دانش‌آموز الزامی است.")
        if not last_name:
            msgs.append("نام خانوادگی دانش‌آموز الزامی است.")

        if not phone or not is_valid_iran_phone(phone):
            msgs.append(f"شماره موبایل «{raw_phone}» معتبر نیست (فرمت صحیح: 0912xxxxxxx).")
        else:
            if phone in seen_phones_in_file:
                msgs.append(
                    f"شماره موبایل تکراری در فایل (تکرار ردیف {seen_phones_in_file[phone]})."
                )
            else:
                seen_phones_in_file[phone] = row_num

            if phone in existing_phones:
                msgs.append("این شماره موبایل قبلاً در سامانه ثبت شده است.")

        if private_code:
            if not private_code.isdigit() or len(private_code) < 5:
                msgs.append("کد ملی / کد اختصاصی باید فقط شامل اعداد (حداقل ۵ رقم) باشد.")
            elif private_code in seen_codes_in_file:
                msgs.append(
                    f"کد ملی/اختصاصی تکراری در فایل (تکرار ردیف {seen_codes_in_file[private_code]})."
                )
            elif private_code in existing_private_codes:
                msgs.append("این کد ملی/اختصاصی قبلاً در سامانه ثبت شده است.")
            else:
                seen_codes_in_file[private_code] = row_num

        if parent_phone and not is_valid_iran_phone(parent_phone):
            msgs.append(f"شماره والدین «{parent_phone_raw}» معتبر نیست.")

        if gender_raw in ("M", "MALE", "مذکر", "پسر", "مرد"):
            gender = User.GenderOfUser.MALE
        elif gender_raw in ("F", "FEMALE", "مونث", "مؤنث", "دختر", "زن"):
            gender = User.GenderOfUser.FEMALE
        else:
            msgs.append(f"جنسیت «{gender_raw}» نامعتبر است (مجاز: M، F، مذکر، مونث).")
            gender = User.GenderOfUser.MALE

        grade_obj = None
        if grade_name:
            grade_obj = grades_by_name.get(grade_name)
            if grade_obj is None:
                msgs.append(f"پایه تحصیلی «{grade_name}» در سیستم تعریف نشده است.")

        major_obj = None
        if major_name:
            major_obj = majors_by_name.get(major_name)
            if major_obj is None:
                msgs.append(f"رشته تحصیلی «{major_name}» در سیستم تعریف نشده است.")

        if msgs:
            row_errors.append(
                {
                    "row": row_num,
                    "phone": raw_phone or "-",
                    "name": full_name,
                    "messages": msgs,
                }
            )
        else:
            prepared_records.append(
                {
                    "phone": phone,
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "private_code": private_code or None,
                    "parent_phone": parent_phone or None,
                    "grade": grade_obj,
                    "major": major_obj,
                    "province": province,
                    "city": city,
                    "target_major_rank": target_major_rank or None,
                    "password": password,
                }
            )

    if default_adviser is not None and not row_errors:
        rem = default_adviser.remaining_capacity()
        if len(prepared_records) > rem:
            row_errors.append(
                {
                    "row": 1,
                    "phone": "-",
                    "name": f"مشاور: {default_adviser}",
                    "messages": [
                        f"ظرفیت باقی‌مانده مشاور انتخابی ({rem} نفر) کمتر از تعداد دانش‌آموزان فایل ({len(prepared_records)} نفر) است."
                    ],
                }
            )

    if row_errors:
        return {
            "success": False,
            "created_count": 0,
            "total_rows": len(rows),
            "errors": row_errors,
            "created_students": [],
        }

    created_students = []
    with transaction.atomic():
        for rec in prepared_records:
            user = User.objects.create_user(
                PhoneNumber=rec["phone"],
                password=rec["password"],
                first_name=rec["first_name"],
                last_name=rec["last_name"],
                gender=rec["gender"],
                type_of_user=User.TypeOfUser.STUDENT,
                private_code=rec["private_code"],
                is_verified=True,
                is_active=True,
            )
            student = Student.objects.create(
                user=user,
                school=school,
                grade=rec["grade"],
                major=rec["major"],
                province=rec["province"],
                city=rec["city"],
                parent_phone_number=rec["parent_phone"],
                adviser=default_adviser,
                target_major_rank=rec["target_major_rank"],
                is_active=True,
            )
            created_students.append(student)

    return {
        "success": True,
        "created_count": len(created_students),
        "total_rows": len(rows),
        "errors": [],
        "created_students": created_students,
    }
