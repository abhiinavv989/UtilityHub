"""Pure utility logic, deliberately separate from Streamlit UI."""
from __future__ import annotations
import base64, csv, hashlib, html, io, json, re, secrets, string, uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote, unquote
import pandas as pd
from PIL import Image, ImageEnhance, ImageOps
from pypdf import PdfReader, PdfWriter

MAX_TEXT_CHARS = 500_000
MAX_IMAGE_PIXELS = 25_000_000

def transform_text(text: str, operation: str, find: str = "", replace: str = "") -> str:
    if operation == "uppercase": return text.upper()
    if operation == "lowercase": return text.lower()
    if operation == "title case": return text.title()
    if operation == "sentence case": return text[:1].upper() + text[1:].lower()
    if operation == "trim whitespace": return "\n".join(line.strip() for line in text.splitlines()).strip()
    if operation == "remove blank lines": return "\n".join(line for line in text.splitlines() if line.strip())
    if operation == "remove duplicate lines":
        return "\n".join(dict.fromkeys(text.splitlines()))
    if operation == "sort lines": return "\n".join(sorted(text.splitlines(), key=str.casefold))
    if operation == "reverse text": return text[::-1]
    if operation == "unique lines": return "\n".join(dict.fromkeys(text.splitlines()))
    if operation == "slug": return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")
    if operation == "find and replace":
        if not find: raise ValueError("Enter text to find.")
        return text.replace(find, replace)
    raise ValueError(f"Unsupported text operation: {operation}")

def text_stats(text: str) -> dict:
    return {"Characters": len(text), "Characters (no spaces)": sum(not c.isspace() for c in text),
            "Words": len(text.split()), "Lines": len(text.splitlines()),
            "Sentences (approx.)": len([x for x in re.split(r"[.!?]+", text) if x.strip()])}

def format_json(raw: str, indent: int = 2, minify: bool = False) -> str:
    obj = json.loads(raw)
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":") if minify else None,
                      indent=None if minify else indent)

def json_to_csv(raw: str) -> str:
    data = json.loads(raw)
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise ValueError("Expected a JSON array containing objects.")
    return pd.DataFrame(data).to_csv(index=False)

def csv_to_json(raw: str) -> str:
    frame = pd.read_csv(io.StringIO(raw))
    return frame.to_json(orient="records", force_ascii=False, indent=2)

def convert_base(value: str, source: str, target: str) -> str:
    bases = {"Binary": 2, "Octal": 8, "Decimal": 10, "Hexadecimal": 16}
    n = int(value.strip(), bases[source])
    return format(n, {2:"b", 8:"o", 10:"d", 16:"X"}[bases[target]])

def convert_unit(value: float, category: str, source: str, target: str) -> float:
    factors = {
        "Length (m)": {"meter":1, "kilometer":1000, "centimeter":.01, "millimeter":.001, "mile":1609.344, "foot":.3048, "inch":.0254},
        "Mass (kg)": {"kilogram":1, "gram":.001, "milligram":.000001, "pound":.45359237, "ounce":.028349523125},
        "Time (seconds)": {"second":1, "minute":60, "hour":3600, "day":86400},
        "Digital storage (bytes)": {"byte":1, "kilobyte (1000 B)":1000, "megabyte (1000 KB)":1e6, "kibibyte (1024 B)":1024, "mebibyte (1024 KiB)":1048576},
        "Area (m²)": {"square meter":1, "square kilometer":1e6, "square foot":.09290304, "acre":4046.8564224, "hectare":10000},
        "Volume (liters)": {"liter":1, "milliliter":.001, "cubic meter":1000, "US gallon":3.785411784},
        "Speed (m/s)": {"meter/second":1, "kilometer/hour":1/3.6, "mile/hour":.44704},
        "Pressure (Pa)": {"pascal":1, "kilopascal":1000, "bar":100000, "atmosphere":101325},
        "Energy (J)": {"joule":1, "kilojoule":1000, "calorie":4.184, "kilowatt-hour":3600000},
        "Power (W)": {"watt":1, "kilowatt":1000, "horsepower":745.699872},
        "Frequency (Hz)": {"hertz":1, "kilohertz":1000, "megahertz":1e6, "gigahertz":1e9},
        "Angle (degrees)": {"degree":1, "radian":180/3.141592653589793},
    }
    if category == "Temperature":
        def to_c(v,u):
            return v if u=="Celsius" else (v-32)*5/9 if u=="Fahrenheit" else v-273.15
        c=to_c(value,source)
        return c if target=="Celsius" else c*9/5+32 if target=="Fahrenheit" else c+273.15
    if category not in factors or source not in factors[category] or target not in factors[category]:
        raise ValueError("Unsupported unit selection.")
    return value*factors[category][source]/factors[category][target]

def percentage(part: float, whole: float) -> float:
    if whole == 0: raise ValueError("The total cannot be zero.")
    return part / whole * 100

def calculate_emi(principal: float, annual_rate: float, months: int) -> float:
    if principal < 0 or annual_rate < 0 or months <= 0: raise ValueError("Use a non-negative principal/rate and positive months.")
    r=annual_rate/1200
    return principal/months if r == 0 else principal*r*(1+r)**months/((1+r)**months-1)

def safe_filename(name: str, default: str = "download") -> str:
    name = Path(name or default).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return (name or default)[:100]

def secure_token(length: int = 32, use_symbols: bool = False) -> str:
    if not 8 <= length <= 256: raise ValueError("Length must be between 8 and 256.")
    chars = string.ascii_letters + string.digits + (string.punctuation if use_symbols else "")
    return "".join(secrets.choice(chars) for _ in range(length))

def digest(data: bytes, algorithm: str = "sha256") -> str:
    if algorithm not in hashlib.algorithms_guaranteed: raise ValueError("Unsupported hash algorithm.")
    return hashlib.new(algorithm, data).hexdigest()

def image_transform(data: bytes, operation: str, width: int = 800, height: int = 600,
                    quality: int = 85, amount: float = 1.0) -> tuple[bytes, str, Image.Image]:
    with Image.open(io.BytesIO(data)) as source:
        if source.width * source.height > MAX_IMAGE_PIXELS: raise ValueError("Image exceeds the 25-megapixel processing limit.")
        im = ImageOps.exif_transpose(source)
        if operation == "resize":
            im.thumbnail((width, height), Image.Resampling.LANCZOS)
        elif operation == "grayscale": im = ImageOps.grayscale(im)
        elif operation == "rotate": im = im.rotate(amount, expand=True)
        elif operation == "flip horizontal": im = ImageOps.mirror(im)
        elif operation == "flip vertical": im = ImageOps.flip(im)
        elif operation == "brightness": im = ImageEnhance.Brightness(im).enhance(amount)
        elif operation == "contrast": im = ImageEnhance.Contrast(im).enhance(amount)
        elif operation not in ("convert PNG", "convert JPEG", "convert WEBP", "compress JPEG"):
            raise ValueError("Unsupported image operation.")
        fmt = "JPEG" if operation in ("convert JPEG", "compress JPEG") else "WEBP" if operation=="convert WEBP" else "PNG" if operation=="convert PNG" else (im.format or "PNG")
        if fmt == "JPEG" and im.mode in ("RGBA","LA","P"):
            background=Image.new("RGB", im.size, "white")
            if im.mode=="P": im=im.convert("RGBA")
            if im.mode in ("RGBA","LA"): background.paste(im, mask=im.getchannel("A"))
            else: background.paste(im.convert("RGB"))
            im=background
        elif fmt in ("JPEG","WEBP") and im.mode not in ("RGB","L"): im=im.convert("RGB")
        out=io.BytesIO()
        im.save(out, format=fmt, quality=quality if fmt in ("JPEG","WEBP") else None, optimize=True)
        return out.getvalue(), fmt.lower(), im.copy()

def pdf_pages(data: bytes) -> int:
    reader=PdfReader(io.BytesIO(data))
    if reader.is_encrypted: raise ValueError("This PDF is encrypted. Unlock it before processing.")
    return len(reader.pages)

def split_pdf(data: bytes, start: int, end: int) -> bytes:
    reader=PdfReader(io.BytesIO(data))
    if reader.is_encrypted: raise ValueError("This PDF is encrypted.")
    if start < 1 or end < start or end > len(reader.pages): raise ValueError("Page range is outside this PDF.")
    writer=PdfWriter()
    for i in range(start-1,end): writer.add_page(reader.pages[i])
    out=io.BytesIO(); writer.write(out); return out.getvalue()

def merge_pdfs(files: list[bytes]) -> bytes:
    if len(files)<2: raise ValueError("Upload at least two PDF files.")
    writer=PdfWriter()
    for data in files:
        reader=PdfReader(io.BytesIO(data))
        if reader.is_encrypted: raise ValueError("One of the PDFs is encrypted.")
        for page in reader.pages: writer.add_page(page)
    out=io.BytesIO(); writer.write(out); return out.getvalue()

def csv_process(data: bytes, operation: str, column: str = "", value: str = "") -> tuple[pd.DataFrame, str]:
    frame=pd.read_csv(io.BytesIO(data))
    original=len(frame)
    if operation=="remove duplicates": frame=frame.drop_duplicates()
    elif operation=="drop missing rows": frame=frame.dropna()
    elif operation=="fill missing":
        if column not in frame.columns: raise ValueError("Choose a valid column.")
        series=frame[column]
        if pd.api.types.is_numeric_dtype(series):
            replacement = series.median() if value=="median" else series.mean() if value=="mean" else 0
        else: replacement = series.mode(dropna=True).iloc[0] if value=="mode" and not series.mode(dropna=True).empty else value
        frame[column]=series.fillna(replacement)
    elif operation=="sort ascending":
        if column not in frame.columns: raise ValueError("Choose a valid column.")
        frame=frame.sort_values(column, kind="stable")
    elif operation=="select columns":
        selected=[x.strip() for x in value.split(",") if x.strip()]
        if not selected or any(x not in frame.columns for x in selected): raise ValueError("Enter valid column names separated by commas.")
        frame=frame[selected]
    elif operation=="rename column":
        if column not in frame.columns or not value.strip(): raise ValueError("Choose a column and enter a new name.")
        if value in frame.columns and value != column: raise ValueError("That column name already exists.")
        frame=frame.rename(columns={column:value.strip()})
    elif operation=="convert numeric":
        if column not in frame.columns: raise ValueError("Choose a valid column.")
        converted=pd.to_numeric(frame[column], errors="coerce")
        invalid=frame[column].notna() & converted.isna()
        if invalid.any(): raise ValueError(f"Cannot convert {int(invalid.sum())} non-empty value(s); original data was kept.")
        frame[column]=converted
    return frame, f"{original} input rows; {len(frame)} output rows; {original-len(frame)} rows removed."
