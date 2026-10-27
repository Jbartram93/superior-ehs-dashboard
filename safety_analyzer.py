"""Safety Alert Excel Analyzer
Run: python safety_analyzer.py
Shows patterns by department, body part, tenure, and type.
"""
import openpyxl, datetime, re
from collections import Counter

path = r"2026 Safety Alert.xlsx"  # Put the file in the same folder as this script
wb = openpyxl.load_workbook(path)
ws = wb["Sheet1"]

incidents = []
for row in ws.iter_rows(min_row=3, values_only=True):
    num, date_str, dept, employee, employer, hire, tenure, itype, desc, body, corrective, notes, comp = row[:13]
    if not date_str or not num: continue
    try:
        dt = datetime.datetime.strptime(str(date_str)[:10], "%m.%d.%y")
        incidents.append({"date": dt, "dept": str(dept).strip() if dept else "", "employee": employee,
            "type": str(itype).strip().lower() if itype else "", "body": str(body).strip() if body else "",
            "tenure": str(tenure).strip() if tenure else ""})
    except: pass

print(f"Total incidents: {len(incidents)}\n")

# By department
dept_counts = Counter(i["dept"] for i in incidents)
print("=== BY DEPARTMENT ===")
for d, c in dept_counts.most_common():
    print(f"  {d:25s} {c}")

print("\n=== BY BODY PART ===")
body_counts = Counter(i["body"] for i in incidents if i["body"])
for b, c in body_counts.most_common():
    print(f"  {b:25s} {c}")

print("\n=== HAND/FINGER INCIDENTS ===")
hand = [i for i in incidents if i["body"] and any(w in i["body"].lower() for w in ["hand","finger","thumb","knuckle","nail","wrist"])]
for i in hand:
    print(f"  {i['date'].strftime('%m/%d')} | {i['dept']:20s} | {i['body']:20s} | {i['type']:15s} | {i['employee']}")
print(f"  Total: {len(hand)}/{len(incidents)} ({len(hand)*100//len(incidents)}%)")

print("\n=== TENURE PATTERNS ===")
tenure_buckets = {"< 1 month": 0, "1-3 months": 0, "3-6 months": 0, "6-12 months": 0, "1-2 years": 0, "2+ years": 0}
for i in incidents:
    t = i["tenure"].lower()
    if any(w in t for w in ["day","week","wk","days","weeks"]): tenure_buckets["< 1 month"] += 1
    elif "month" in t or "mo" in t:
        nums = re.findall(r"\d+", t)
        n = int(nums[0]) if nums else 0
        if n <= 3: tenure_buckets["1-3 months"] += 1
        elif n <= 6: tenure_buckets["3-6 months"] += 1
        elif n <= 12: tenure_buckets["6-12 months"] += 1
        else: tenure_buckets["1-2 years"] += 1
    elif any(w in t for w in ["yr","year"]): tenure_buckets["2+ years"] += 1
    else: tenure_buckets["1-3 months"] += 1
for b, c in tenure_buckets.items():
    print(f"  {b:15s} {c}")
