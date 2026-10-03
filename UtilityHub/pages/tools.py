import base64, difflib, html, io, json, math, random, re, secrets, string, uuid
from datetime import date, datetime, time
from zoneinfo import ZoneInfo, available_timezones
import pandas as pd
import qrcode
import streamlit as st
from PIL import Image
from utils.core import *
from utils.registry import TOOLS

def run_tool(name):
    funcs = {
        "Text workbench": text_workbench, "Text comparison": text_comparison,
        "JSON formatter / validator": json_tool, "JSON to CSV": json_csv,
        "CSV to JSON": csv_json, "Base64 & URL encoder": encoding_tool,
        "Hash generator": hash_tool, "UUID & secure token": token_tool,
        "Regex tester": regex_tool, "Calculator": calculator_tool,
        "Percentage calculator": percentage_tool, "Discount & GST": discount_tool,
        "Simple & compound interest": interest_tool, "Loan EMI estimator": emi_tool,
        "Age & date difference": dates_tool, "Average / median / range": stats_tool,
        "Unit converter": unit_tool, "Number base converter": base_tool,
        "QR code generator": qr_tool, "Password generator": password_tool,
        "Random generator": random_tool, "Color tools": color_tool,
        "Lorem ipsum": lorem_tool, "CSV workbench": csv_tool,
        "Sample data generator": sample_tool, "Notes & checklist": notes_tool,
        "Pomodoro planner": pomodoro_tool, "Time-zone converter": timezone_tool,
        "Merge PDFs": merge_pdf_tool, "Split PDF": split_pdf_tool,
        "PDF metadata": pdf_meta_tool, "PDF text extractor": pdf_text_tool,
        "Images to PDF": images_pdf_tool, "Text file maker": text_file_tool,
        "Image inspector": image_info_tool, "Image resize": image_resize_tool,
        "Image conversion": image_convert_tool, "Image effects": image_effect_tool,
        "About UtilityHub": about_tool,
    }
    funcs.get(name, about_tool)()

def text_workbench():
    st.subheader("Text workbench")
    st.write("Transform text, clean lines, and inspect basic text statistics locally.")
    raw=st.text_area("Input text", height=180, key="text_input")
    op=st.selectbox("Operation",["uppercase","lowercase","title case","sentence case","trim whitespace","remove blank lines","remove duplicate lines","sort lines","reverse text","unique lines","slug","find and replace"])
    c1,c2=st.columns(2)
    find=c1.text_input("Find",key="find_text") if op=="find and replace" else ""
    repl=c2.text_input("Replace with",key="replace_text") if op=="find and replace" else ""
    if st.button("Process text",type="primary"):
        try:
            result=transform_text(raw,op,find,repl)
            st.text_area("Result",result,height=180,key="text_result")
            st.download_button("Download result",result.encode(),file_name="text_result.txt",mime="text/plain")
            st.json(text_stats(raw))
        except ValueError as e: st.error(str(e))
    else:
        st.caption("Sentence count is approximate and punctuation-based.")

def text_comparison():
    st.subheader("Text comparison")
    a,b=st.columns(2)
    left=a.text_area("Original text",height=220); right=b.text_area("New text",height=220)
    if st.button("Compare text",type="primary"):
        diff="\n".join(difflib.unified_diff(left.splitlines(),right.splitlines(),fromfile="original",tofile="new",lineterm=""))
        st.code(diff or "No differences found.",language="diff")
        st.download_button("Download diff",diff.encode(),file_name="text_diff.txt")

def json_tool():
    st.subheader("JSON formatter and validator")
    raw=st.text_area("JSON input",height=240,placeholder='{"name":"UtilityHub","ready":true}')
    c1,c2=st.columns(2); indent=c1.selectbox("Indentation",[2,4, tabs:=1],format_func=lambda x:"Tabs" if x==1 else str(x)); mini=c2.checkbox("Minify")
    if st.button("Validate and format",type="primary"):
        try:
            result=format_json(raw,indent,mini); st.success("Valid JSON"); st.code(result,language="json")
            st.download_button("Download JSON",result.encode(),file_name="formatted.json",mime="application/json")
        except (json.JSONDecodeError,ValueError) as e: st.error(f"Invalid JSON: {e}")

def json_csv():
    st.subheader("JSON to CSV")
    raw=st.text_area("JSON array of objects",height=220,placeholder='[{"name":"A","score":4},{"name":"B","score":7}]')
    if st.button("Convert to CSV",type="primary"):
        try:
            result=json_to_csv(raw); st.code(result[:12000]); st.download_button("Download CSV",result.encode(),file_name="converted.csv",mime="text/csv")
        except Exception as e: st.error(str(e))

def csv_json():
    st.subheader("CSV to JSON")
    raw=st.text_area("CSV input",height=220,placeholder="name,score\nA,4\nB,7")
    if st.button("Convert to JSON",type="primary"):
        try:
            result=csv_to_json(raw); st.code(result,language="json"); st.download_button("Download JSON",result.encode(),file_name="converted.json",mime="application/json")
        except Exception as e: st.error(f"Could not convert CSV: {e}")

def encoding_tool():
    st.subheader("Base64 and URL encoding")
    mode=st.radio("Mode",["Base64 encode","Base64 decode","URL encode","URL decode"],horizontal=True)
    raw=st.text_area("Text")
    if st.button("Convert",type="primary"):
        try:
            if mode=="Base64 encode": out=base64.b64encode(raw.encode()).decode()
            elif mode=="Base64 decode": out=base64.b64decode(raw,validate=True).decode("utf-8")
            elif mode=="URL encode": out=quote(raw,safe="")
            else: out=unquote(raw)
            st.text_area("Result",out); st.download_button("Download result",out.encode(),file_name="converted.txt")
        except Exception as e: st.error(f"Unable to convert input: {e}")

def hash_tool():
    st.subheader("Hash generator")
    raw=st.text_area("Text to hash",max_chars=MAX_TEXT_CHARS)
    algo=st.selectbox("Algorithm",sorted(hashlib.algorithms_guaranteed))
    if st.button("Generate hash",type="primary"):
        out=digest(raw.encode(),algo); st.code(out); st.caption("A hash is a one-way digest, not encryption.")

def token_tool():
    st.subheader("UUID and secure token")
    st.code(str(uuid.uuid4()))
    length=st.slider("Token length",8,128,32); symbols=st.checkbox("Include symbols")
    if st.button("Generate token",type="primary"):
        st.code(secure_token(length,symbols))
        st.caption("Generated values are not stored by this application.")

def regex_tool():
    st.subheader("Regular expression tester")
    pattern=st.text_input("Pattern",placeholder=r"\b[A-Z]\w+")
    sample=st.text_area("Test text",max_chars=20000)
    if st.button("Test pattern",type="primary"):
        try:
            matches=list(re.finditer(pattern,sample))
            st.write(f"{len(matches)} match(es)")
            for m in matches[:200]: st.code(f"{m.start()}–{m.end()}: {m.group(0)!r}")
            if len(matches)>200: st.info("Only the first 200 matches are shown.")
        except re.error as e: st.error(f"Invalid regular expression: {e}")
        st.caption("Use trusted, simple patterns. Input is capped, but complex patterns may still consume resources.")

def calculator_tool():
    st.subheader("Basic calculator")
    st.caption("Supported: numbers, +, -, *, /, parentheses, and decimals. No Python code is executed.")
    a=st.number_input("First number",value=0.0,key="calc_a"); op=st.selectbox("Operation",["+","−","×","÷"]); b=st.number_input("Second number",value=1.0,key="calc_b")
    if st.button("Calculate",type="primary"):
        if op=="÷" and b==0: st.error("Cannot divide by zero.")
        else: st.metric("Result",a+b if op=="+" else a-b if op=="−" else a*b if op=="×" else a/b)

def percentage_tool():
    st.subheader("Percentage calculator")
    part=st.number_input("Part",value=25.0); whole=st.number_input("Total",value=100.0)
    if st.button("Calculate percentage",type="primary"):
        try: st.metric("Percentage",f"{percentage(part,whole):.4g}%")
        except ValueError as e: st.error(str(e))

def discount_tool():
    st.subheader("Discount and GST calculator")
    price=st.number_input("Original price",min_value=0.0,value=1000.0); disc=st.number_input("Discount (%)",0.0,100.0,10.0); gst=st.number_input("GST (%)",0.0,100.0,18.0)
    discounted=price*(1-disc/100); total=discounted*(1+gst/100)
    st.metric("After discount, before GST",f"₹{discounted:,.2f}"); st.metric("Estimated final price",f"₹{total:,.2f}")

def interest_tool():
    st.subheader("Simple and compound interest")
    p=st.number_input("Principal",min_value=0.0,value=10000.0); rate=st.number_input("Annual rate (%)",min_value=0.0,value=7.0); years=st.number_input("Years",min_value=0.0,value=2.0); comp=st.selectbox("Method",["Simple","Compound"])
    amount=p*(1+rate*years/100) if comp=="Simple" else p*(1+rate/100)**years
    st.metric("Estimated final amount",f"₹{amount:,.2f}"); st.metric("Interest",f"₹{amount-p:,.2f}")

def emi_tool():
    st.subheader("Loan EMI estimator")
    p=st.number_input("Loan principal (₹)",min_value=0.0,value=500000.0); r=st.number_input("Annual interest rate (%)",min_value=0.0,value=8.5); months=st.number_input("Term (months)",min_value=1,max_value=600,value=60)
    try:
        emi=calculate_emi(p,r,int(months)); st.metric("Estimated monthly EMI",f"₹{emi:,.2f}"); st.write(f"Total payment: ₹{emi*months:,.2f} · Estimated interest: ₹{emi*months-p:,.2f}")
    except ValueError as e: st.error(str(e))
    st.caption("Illustrative estimate only; fees and lender terms are not included.")

def dates_tool():
    st.subheader("Age and date difference")
    d1=st.date_input("Earlier date",value=date(2000,1,1)); d2=st.date_input("Later date",value=date.today())
    if d2<d1: st.error("Later date must be on or after earlier date.")
    else: st.metric("Days between dates",(d2-d1).days); st.write(f"Approximate years: {(d2-d1).days/365.2425:.2f}")

def stats_tool():
    st.subheader("Average, median, minimum, maximum")
    raw=st.text_input("Numbers separated by commas",placeholder="12, 8, 17, 4")
    if st.button("Calculate statistics",type="primary"):
        try:
            nums=[float(x.strip()) for x in raw.split(",") if x.strip()]
            if not nums: raise ValueError("Enter at least one number.")
            st.json({"count":len(nums),"mean":sum(nums)/len(nums),"median":float(pd.Series(nums).median()),"minimum":min(nums),"maximum":max(nums),"range":max(nums)-min(nums)})
        except ValueError as e: st.error(f"Enter valid numbers. {e}")

def unit_tool():
    st.subheader("Unit converter")
    category=st.selectbox("Category",["Length (m)","Mass (kg)","Temperature","Area (m²)","Volume (liters)","Speed (m/s)","Time (seconds)","Digital storage (bytes)","Pressure (Pa)","Energy (J)","Power (W)","Frequency (Hz)","Angle (degrees)"])
    choices={"Length (m)":["meter","kilometer","centimeter","millimeter","mile","foot","inch"],"Mass (kg)":["kilogram","gram","milligram","pound","ounce"],"Temperature":["Celsius","Fahrenheit","Kelvin"],"Area (m²)":["square meter","square kilometer","square foot","acre","hectare"],"Volume (liters)":["liter","milliliter","cubic meter","US gallon"],"Speed (m/s)":["meter/second","kilometer/hour","mile/hour"],"Time (seconds)":["second","minute","hour","day"],"Digital storage (bytes)":["byte","kilobyte (1000 B)","megabyte (1000 KB)","kibibyte (1024 B)","mebibyte (1024 KiB)"],"Pressure (Pa)":["pascal","kilopascal","bar","atmosphere"],"Energy (J)":["joule","kilojoule","calorie","kilowatt-hour"],"Power (W)":["watt","kilowatt","horsepower"],"Frequency (Hz)":["hertz","kilohertz","megahertz","gigahertz"],"Angle (degrees)":["degree","radian"]}
    c1,c2=st.columns(2); src=c1.selectbox("From",choices[category]); dst=c2.selectbox("To",choices[category],index=min(1,len(choices[category])-1)); val=st.number_input("Value",value=1.0)
    if st.button("Convert",type="primary"):
        try: st.metric("Converted value",f"{convert_unit(val,category,src,dst):,.8g} {dst}")
        except ValueError as e: st.error(str(e))

def base_tool():
    st.subheader("Number base converter")
    val=st.text_input("Integer",value="1010"); src=st.selectbox("Input base",["Binary","Octal","Decimal","Hexadecimal"]); dst=st.selectbox("Output base",["Binary","Octal","Decimal","Hexadecimal"],index=2)
    if st.button("Convert base",type="primary"):
        try: st.code(convert_base(val,src,dst))
        except ValueError: st.error(f"Enter a valid {src.lower()} integer.")

def qr_tool():
    st.subheader("QR code generator")
    raw=st.text_area("Text or URL to encode",placeholder="https://example.com")
    if st.button("Generate QR code",type="primary"):
        if not raw.strip(): st.warning("Enter text or a URL first.")
        else:
            qr=qrcode.QRCode(box_size=8,border=4); qr.add_data(raw.strip()); qr.make(fit=True); im=qr.make_image(fill_color="black",back_color="white")
            buf=io.BytesIO(); im.save(buf,format="PNG"); st.image(buf.getvalue(),width=260); st.download_button("Download QR PNG",buf.getvalue(),file_name="qrcode.png",mime="image/png")
    st.caption("Avoid encoding passwords or other sensitive information into QR codes shared publicly.")

def password_tool():
    st.subheader("Password generator")
    length=st.slider("Length",8,128,20); lower=st.checkbox("Lowercase",True); upper=st.checkbox("Uppercase",True); digits=st.checkbox("Digits",True); symbols=st.checkbox("Symbols",True)
    if st.button("Generate password",type="primary"):
        chars=(string.ascii_lowercase if lower else "")+(string.ascii_uppercase if upper else "")+(string.digits if digits else "")+(string.punctuation if symbols else "")
        if not chars: st.error("Select at least one character group.")
        else: st.code("".join(secrets.choice(chars) for _ in range(length)))

def random_tool():
    st.subheader("Random number or choice")
    mode=st.radio("Generator",["Integer","Decimal","Choose from list"],horizontal=True)
    if mode=="Integer":
        lo=st.number_input("Minimum",value=1,step=1); hi=st.number_input("Maximum",value=100,step=1)
        if st.button("Generate",type="primary"):
            if lo>hi: st.error("Minimum must not exceed maximum.")
            else: st.metric("Result",secrets.randbelow(int(hi-lo+1))+int(lo))
    elif mode=="Decimal":
        lo=st.number_input("Lower bound",value=0.0); hi=st.number_input("Upper bound",value=1.0)
        if st.button("Generate decimal",type="primary"):
            if lo>hi: st.error("Lower bound must not exceed upper bound.")
            else: st.metric("Result",secrets.SystemRandom().uniform(lo,hi))
    else:
        raw=st.text_area("One choice per line")
        if st.button("Choose",type="primary"):
            options=[x for x in raw.splitlines() if x.strip()]
            if not options: st.error("Enter at least one option.")
            else: st.success(secrets.choice(options))

def color_tool():
    st.subheader("HEX and RGB color converter")
    hx=st.color_picker("Choose a color",value="#4F46E5")
    r,g,b=tuple(bytes.fromhex(hx.lstrip("#")))
    st.code(f"HEX: {hx.upper()}\nRGB: ({r}, {g}, {b})")
    st.markdown(f'<div style="height:70px;border-radius:12px;background:{hx};border:1px solid #ddd"></div>',unsafe_allow_html=True)

def lorem_tool():
    st.subheader("Lorem ipsum generator")
    count=st.slider("Paragraphs",1,10,3)
    paragraph="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer vitae lectus non urna tempor volutpat. Sed consequat, neque at facilisis luctus, velit sem blandit sapien, vitae feugiat erat magna sed justo."
    result="\n\n".join(paragraph for _ in range(count))
    st.text_area("Generated text",result,height=180)
    st.download_button("Download text",result.encode(),file_name="lorem.txt")

def csv_tool():
    st.subheader("CSV workbench")
    uploaded=st.file_uploader("Upload CSV",type=["csv"],key="csv_workbench_upload")
    if not uploaded: st.info("Upload a CSV to preview and transform it. Maximum upload size: 25 MB."); return
    if uploaded.size>25*1024*1024: st.error("File exceeds the 25 MB limit."); return
    try: df=pd.read_csv(uploaded)
    except Exception as e: st.error(f"Could not read CSV. Check the delimiter, encoding, and file structure. Details: {e}"); return
    st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
    st.dataframe(df.head(st.slider("Preview rows",5,100,20)),use_container_width=True)
    st.json({"missing values per column":{str(k):int(v) for k,v in df.isna().sum().items()},"duplicate rows":int(df.duplicated().sum())})
    op=st.selectbox("Transformation",["none","remove duplicates","drop missing rows","fill missing","sort ascending","select columns","rename column","convert numeric"])
    col=st.selectbox("Column (when required)",list(df.columns)) if len(df.columns) else ""
    value=st.text_input("Value / new name / comma-separated column list",key="csv_transform_value")
    if op=="fill missing": value=st.selectbox("Fill method",["median","mean","0","mode","custom"])
    if st.button("Apply transformation",type="primary"):
        try:
            result,summary=csv_process(uploaded.getvalue(),op,col,value)
            st.success(summary); st.dataframe(result.head(100),use_container_width=True)
            st.download_button("Download processed CSV",result.to_csv(index=False).encode("utf-8"),file_name="processed.csv",mime="text/csv")
        except Exception as e: st.error(f"Transformation failed: {e}. The original upload was not changed.")

def sample_tool():
    st.subheader("Sample CSV / JSON generator")
    rows=st.slider("Rows",1,500,20); kind=st.selectbox("Format",["CSV","JSON"])
    if st.button("Generate sample data",type="primary"):
        data=[{"id":i+1,"name":f"Person {i+1}","score":(i*17)%101,"active":i%2==0} for i in range(rows)]
        out=pd.DataFrame(data).to_csv(index=False) if kind=="CSV" else json.dumps(data,indent=2)
        st.code(out[:8000],language="json" if kind=="JSON" else "text")
        st.download_button("Download sample",out.encode(),file_name=f"sample.{kind.lower()}",mime="text/csv" if kind=="CSV" else "application/json")

def notes_tool():
    st.subheader("Session notes and checklist")
    st.caption("Notes and tasks are temporary and may disappear when the session ends or the app restarts.")
    st.session_state.setdefault("uh_notes",""); st.session_state.setdefault("uh_tasks",[])
    st.session_state["uh_notes"]=st.text_area("Notes",value=st.session_state["uh_notes"],height=180,key="notes_area")
    task=st.text_input("New task",key="new_task")
    if st.button("Add task") and task.strip():
        st.session_state["uh_tasks"].append({"text":task.strip(),"done":False}); st.rerun()
    for i,t in enumerate(st.session_state["uh_tasks"]):
        t["done"]=st.checkbox(t["text"],value=t["done"],key=f"task_{i}")
    if st.button("Clear tasks"): st.session_state["uh_tasks"]=[]; st.rerun()
    export=st.session_state["uh_notes"]+"\n\n"+ "\n".join(("[x] " if t["done"] else "[ ] ")+t["text"] for t in st.session_state["uh_tasks"])
    st.download_button("Export notes and checklist",export.encode(),file_name="notes.txt")

def pomodoro_tool():
    st.subheader("Pomodoro study planner")
    work=st.number_input("Focus interval (minutes)",min_value=1,max_value=180,value=25); rest=st.number_input("Short break (minutes)",min_value=1,max_value=60,value=5); cycles=st.number_input("Number of cycles",min_value=1,max_value=20,value=4)
    st.metric("Planned focus time",f"{work*cycles} minutes"); st.metric("Planned short breaks",f"{rest*max(0,cycles-1)} minutes")
    st.info("This is a session planner, not a background timer. Streamlit cannot guarantee notifications while the browser is closed.")

def timezone_tool():
    st.subheader("Time-zone converter")
    c1,c2=st.columns(2)
    src=c1.selectbox("From time zone",["Asia/Kolkata","UTC","America/New_York","Europe/London","Asia/Tokyo"])
    dst=c2.selectbox("To time zone",["UTC","Asia/Kolkata","America/New_York","Europe/London","Asia/Tokyo"],index=0)
    picked_date=st.date_input("Local date", value=date.today())
    picked_time=st.time_input("Local time", value=datetime.now().time().replace(second=0, microsecond=0))
    dt=datetime.combine(picked_date, picked_time)
    if st.button("Convert time",type="primary"):
        try:
            aware=dt.replace(tzinfo=ZoneInfo(src)); result=aware.astimezone(ZoneInfo(dst))
            st.success(result.strftime("%Y-%m-%d %H:%M:%S %Z (%z)"))
            st.caption("Ambiguous/nonexistent daylight-saving times may need manual review.")
        except Exception as e: st.error(f"Could not convert time: {e}")

def merge_pdf_tool():
    st.subheader("Merge PDFs")
    files=st.file_uploader("Select at least two PDF files",type=["pdf"],accept_multiple_files=True)
    if st.button("Merge PDFs",type="primary"):
        try:
            result=merge_pdfs([f.getvalue() for f in files or []]); st.success("PDFs merged.")
            st.download_button("Download merged PDF",result,file_name="merged.pdf",mime="application/pdf")
        except Exception as e: st.error(f"Could not merge PDFs: {e}")

def split_pdf_tool():
    st.subheader("Split PDF by page range")
    f=st.file_uploader("PDF file",type=["pdf"],key="split_pdf")
    if f:
        try: pages=pdf_pages(f.getvalue()); st.caption(f"{pages} page(s) found.")
        except Exception as e: st.error(str(e)); return
        a,b=st.columns(2); start=a.number_input("First page",1,pages,1); end=b.number_input("Last page",1,pages,pages)
        if st.button("Export page range",type="primary"):
            try: out=split_pdf(f.getvalue(),int(start),int(end)); st.download_button("Download selected pages",out,file_name="pages.pdf",mime="application/pdf")
            except Exception as e: st.error(str(e))

def pdf_meta_tool():
    st.subheader("PDF metadata")
    f=st.file_uploader("PDF file",type=["pdf"],key="meta_pdf")
    if f:
        try:
            reader=PdfReader(io.BytesIO(f.getvalue()))
            if reader.is_encrypted: st.error("This PDF is encrypted.")
            else: st.json({"pages":len(reader.pages),"metadata":{str(k):str(v) for k,v in (reader.metadata or {}).items()}})
        except Exception as e: st.error(f"Invalid PDF: {e}")

def pdf_text_tool():
    st.subheader("PDF text extractor")
    f=st.file_uploader("Text-based PDF",type=["pdf"],key="text_pdf")
    if f:
        try:
            reader=PdfReader(io.BytesIO(f.getvalue()))
            if reader.is_encrypted: st.error("This PDF is encrypted.")
            else:
                out="\n\n".join(p.extract_text() or "" for p in reader.pages)
                if not out.strip(): st.warning("No selectable text found. Scanned PDFs require OCR, which is not included.")
                st.text_area("Extracted text",out,height=260)
                st.download_button("Download extracted text",out.encode(),file_name="extracted.txt")
        except Exception as e: st.error(f"Could not read PDF: {e}")

def images_pdf_tool():
    st.subheader("Images to PDF")
    files=st.file_uploader("Upload images",type=["png","jpg","jpeg","webp"],accept_multiple_files=True,key="images_pdf")
    if st.button("Create PDF",type="primary"):
        try:
            if not files: raise ValueError("Upload at least one image.")
            images=[]
            for f in files:
                im=Image.open(io.BytesIO(f.getvalue())).convert("RGB"); images.append(im)
            out=io.BytesIO(); images[0].save(out,format="PDF",save_all=True,append_images=images[1:])
            st.download_button("Download PDF",out.getvalue(),file_name="images.pdf",mime="application/pdf")
        except Exception as e: st.error(f"Could not create PDF: {e}")

def text_file_tool():
    st.subheader("Text file maker")
    content=st.text_area("Text to save",height=220)
    filename=st.text_input("File name",value="notes.txt")
    st.download_button("Download text file",content.encode("utf-8"),file_name=safe_filename(filename,"notes.txt"),mime="text/plain")

def _image_upload(key):
    f=st.file_uploader("Upload image",type=["png","jpg","jpeg","webp","bmp"],key=key)
    if f and f.size>15*1024*1024: st.error("Image exceeds 15 MB."); return None
    return f

def image_info_tool():
    st.subheader("Image inspector")
    f=_image_upload("img_info")
    if f:
        try:
            im=Image.open(io.BytesIO(f.getvalue()))
            st.image(im,caption=f.name,use_container_width=True)
            st.json({"width":im.width,"height":im.height,"mode":im.mode,"format":im.format,"file size bytes":f.size})
        except Exception as e: st.error(f"Invalid image: {e}")

def image_resize_tool():
    st.subheader("Image resize")
    f=_image_upload("img_resize")
    if f:
        try:
            im=Image.open(io.BytesIO(f.getvalue())); c1,c2=st.columns(2)
            w=c1.number_input("Maximum width",1,8000,min(800,im.width)); h=c2.number_input("Maximum height",1,8000,min(600,im.height))
            if st.button("Resize image",type="primary"):
                out,fmt,preview=image_transform(f.getvalue(),"resize",int(w),int(h))
                st.image(preview,caption=f"Output: {preview.width} × {preview.height}")
                st.download_button("Download resized image",out,file_name=f"resized.{fmt}",mime=f"image/{fmt}")
        except Exception as e: st.error(f"Could not resize image: {e}")

def image_convert_tool():
    st.subheader("Image conversion")
    f=_image_upload("img_convert")
    fmt=st.selectbox("Output format",["PNG","JPEG","WEBP"])
    quality=st.slider("Quality (JPEG/WebP)",10,100,85)
    if f and st.button("Convert image",type="primary"):
        try:
            out,ext,preview=image_transform(f.getvalue(),"convert "+fmt,quality=quality)
            st.image(preview); st.download_button("Download converted image",out,file_name=f"converted.{ext}",mime=f"image/{ext}")
        except Exception as e: st.error(f"Could not convert image: {e}")

def image_effect_tool():
    st.subheader("Image effects")
    f=_image_upload("img_effect")
    op=st.selectbox("Effect",["grayscale","rotate","flip horizontal","flip vertical","brightness","contrast"])
    amount=st.slider("Rotation degrees", -180,180,90) if op=="rotate" else st.slider("Adjustment",0.1,2.0,1.2,0.1) if op in ("brightness","contrast") else 1.0
    if f and st.button("Apply effect",type="primary"):
        try:
            out,fmt,preview=image_transform(f.getvalue(),op,amount=amount)
            st.image(preview); st.download_button("Download result",out,file_name=f"edited.{fmt}",mime=f"image/{fmt}")
        except Exception as e: st.error(f"Could not edit image: {e}")

def about_tool():
    st.subheader("About UtilityHub")
    st.write("UtilityHub is a local-first collection of everyday tools built with Python and Streamlit. File transformations are performed by this application in memory; no database or external API is required.")
    st.warning("Privacy depends on the hosting provider and deployment configuration. Do not upload confidential files, passwords, or sensitive personal information to a public deployment.")
    st.markdown("**Limits:** uploads are capped at 25 MB by Streamlit configuration; individual image tools apply smaller limits. Scanned-PDF OCR, DOCX/PDF fidelity conversion, live currency rates, account sync, and notifications while the browser is closed are not included.")
    st.markdown("**Supported areas:** PDF basics, image processing, text, developer helpers, calculators, unit conversion, QR/generators, CSV, and session productivity.")
