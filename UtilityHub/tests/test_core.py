import io, json
import pandas as pd
import pytest
from PIL import Image
from utils.core import *

def test_text_transformations():
    assert transform_text("a\nb\na","remove duplicate lines")=="a\nb"
    assert transform_text("Hello World","slug")=="hello-world"
    assert transform_text(" a \n b ","trim whitespace")=="a\nb"

def test_text_stats_empty():
    assert text_stats("")["Words"]==0

def test_json_format_and_invalid():
    assert format_json('{"a":1}')=='{\n  "a": 1\n}'
    with pytest.raises(json.JSONDecodeError): format_json("{oops}")

def test_number_base_conversion():
    assert convert_base("1010","Binary","Decimal")=="10"
    assert convert_base("ff","Hexadecimal","Binary")=="11111111"
    with pytest.raises(ValueError): convert_base("2","Binary","Decimal")

def test_unit_conversions():
    assert convert_unit(1,"Length (m)","kilometer","meter")==1000
    assert convert_unit(0,"Temperature","Celsius","Fahrenheit")==32

def test_calculators():
    assert percentage(25,100)==25
    assert calculate_emi(12000,0,12)==1000
    with pytest.raises(ValueError): percentage(1,0)

def test_safe_filename():
    assert safe_filename("../../my file?.txt")=="my_file_.txt"

def test_csv_transformations():
    raw=b"a,b\n1,x\n1,x\n, y\n"
    result,summary=csv_process(raw,"remove duplicates")
    assert len(result)==2
    assert "rows removed" in summary

def test_csv_numeric_conversion_fails_safely():
    with pytest.raises(ValueError): csv_process(b"score\n1\nbad\n","convert numeric","score")

def test_image_conversion_and_resize():
    buf=io.BytesIO()
    im=Image.new("RGBA",(40,20),(255,0,0,100)); im.save(buf,format="PNG")
    out,fmt,preview=image_transform(buf.getvalue(),"convert JPEG",quality=80)
    assert fmt=="jpeg" and preview.mode=="RGB"
    resized,_,small=image_transform(buf.getvalue(),"resize",20,20)
    assert small.size==(20,10)

def test_pdf_page_range_validation():
    from pypdf import PdfWriter
    buf=io.BytesIO(); w=PdfWriter(); w.add_blank_page(width=72,height=72); w.write(buf)
    assert pdf_pages(buf.getvalue())==1
    with pytest.raises(ValueError): split_pdf(buf.getvalue(),0,1)
    assert len(PdfReader(io.BytesIO(split_pdf(buf.getvalue(),1,1))).pages)==1
