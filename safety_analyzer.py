"""Superior EHS Safety Analyzer
Interactive analysis of 2026 Safety Alert data.
Run: python safety_analyzer.py
Shows patterns by department, body part, tenure, type.
No employee names in output.
"""
import openpyxl, datetime, re, sys
from collections import Counter, defaultdict

def load_data(filepath="2026 Safety Alert.xlsx"):
    """Load incidents from Excel. Returns list of dicts."""
    wb = openpyxl.load_workbook(filepath)
    ws = wb["Sheet1"]
    incidents = []
    for row in ws.iter_rows(min_row=3, values_only=True):
        num, date_str, dept, _, _, hire, tenure, itype, desc, body = row[:10]
        if not date_str or not num: continue
        try:
            dt = datetime.datetime.strptime(str(date_str)[:10], "%m.%d.%y")
            t = str(tenure).strip() if tenure else ""
            incidents.append({
                "date": dt,
                "month": dt.strftime("%b"),
                "month_num": dt.month,
                "dept": str(dept).strip() if dept else "Unknown",
                "type": str(itype).strip().lower() if itype else "unknown",
                "body": str(body).strip() if body else "Unknown",
                "tenure_raw": t,
            })
        except:
            pass
    return incidents

def tenure_bucket(t):
    """Classify tenure string into a bucket."""
    t = t.lower()
    if "yr" in t or "year" in t: return "2+ years"
    m = re.search(r'(\d+)\s*(?:mo|month)', t)
    if m:
        months = int(m.group(1))
        w = re.search(r'(\d+)\s*(?:wk|week)', t)
        d = re.search(r'(\d+)\s*(?:day)', t)
        extra = 0
        if w and int(w.group(1)) >= 2: extra = 1
        if d and int(d.group(1)) >= 14: extra = 1
        total = months + extra
        if total <= 1: return "< 1 month"
        elif total <= 3: return "1-3 months"
        elif total <= 6: return "3-6 months"
        elif total <= 12: return "6-12 months"
        elif total <= 24: return "1-2 years"
        else: return "2+ years"
    if "wk" in t or "week" in t or "day" in t: return "< 1 month"
    return "1-3 months"

def is_hand(body):
    """Check if body part involves hand/finger."""
    b = body.lower()
    return any(w in b for w in ["hand", "finger", "thumb", "knuckle", "wrist"])

def is_recordable(itype):
    """Check if incident type is a recordable."""
    return "loss" in itype or "recordable" in itype or "lost" in itype

def print_section(title, data, value_key="count"):
    """Print a formatted section."""
    print(f"\n=== {title} ===")
    if not data:
        print("  (no data)")
        return
    total = sum(v if isinstance(v, int) else v["count"] for v in data.values()) if isinstance(data, dict) else sum(v for v in data.values())
    for key, val in sorted(data.items(), key=lambda x: -x[1] if isinstance(x[1], int) else -x[1]["count"]):
        if isinstance(val, int):
            pct = val / total * 100 if total else 0
            bar = "\u2588" * int(pct / 4) + "\u2581" * (1 if pct % 4 > 1 else 0)
            print(f"  {key:25s} {val:3d}  {pct:5.1f}%  {bar}")
        else:
            print(f"  {key:25s} {val['count']:3d}")

def analyze(incidents, title_filter=None, dept_filter=None, tenure_filter=None, type_filter=None):
    """Run analysis with optional filters."""
    filtered = incidents
    if dept_filter:
        filtered = [i for i in filtered if dept_filter.lower() in i["dept"].lower()]
    if tenure_filter:
        filtered = [i for i in filtered if tenure_bucket(i["tenure_raw"]) == tenure_filter]
    if type_filter:
        filtered = [i for i in filtered if type_filter.lower() in i["type"].lower()]

    print(f"\n{'='*60}")
    print(f"  SUPERIOR EHS ANALYSIS")
    filters_on = [f"{k}={v}" for k, v in [("Dept", dept_filter), ("Tenure", tenure_filter), ("Type", type_filter)] if v]
    print(f"  Total incidents: {len(filtered)}" + (f"  [{', '.join(filters_on)}]" if filters_on else ""))
    print(f"{'='*60}")

    # Department breakdown
    dept_counts = Counter(i["dept"] for i in filtered)
    print_section("BY DEPARTMENT", dept_counts)

    # Body part (aggregated)
    body_parts = Counter()
    hand_count = 0
    for i in filtered:
        if is_hand(i["body"]):
            body_parts["Hand / Finger"] = body_parts.get("Hand / Finger", 0) + 1
            hand_count += 1
        else:
            bp = i["body"].split(",")[0].strip().title()[:20]
            body_parts[bp] = body_parts.get(bp, 0) + 1
    print_section("BY BODY PART", body_parts)
    print(f"  Hand/finger incidents: {hand_count}/{len(filtered)} ({hand_count/len(filtered)*100:.0f}%)" if filtered else "")

    # Tenure breakdown
    tenure_counts = Counter()
    for i in filtered:
        tenure_counts[tenure_bucket(i["tenure_raw"])] += 1
    print_section("BY TENURE", tenure_counts)

    # Monthly trend
    monthly = Counter(i["month"] for i in filtered)
    months_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    print("\n=== BY MONTH ===")
    for m in months_order:
        if monthly[m]:
            bar = "\u2588" * monthly[m]
            print(f"  {m:6s} {monthly[m]:3d}  {bar}")

    # Recordables
    recordables = [i for i in filtered if is_recordable(i["type"])]
    if recordables:
        print(f"\n=== RECORDABLES ({len(recordables)}) ===")
        for i in recordables:
            print(f"  {i['date'].strftime('%b %d'):8s} | {i['dept']:18s} | {i['type']:12s} | {i['body']}")
    else:
        print(f"\n=== RECORDABLES: None in filtered set ===")

    # Recordable rate estimate
    rec_count = len([i for i in filtered if is_recordable(i["type"])])
    print(f"\n  Recordables: {rec_count} / {len(filtered)} incidents ({rec_count/len(filtered)*100:.0f}%)" if filtered else "")

    return filtered

# ===== MAIN =====
if __name__ == "__main__":
    filepath = "2026 Safety Alert.xlsx"
    incidents = load_data(filepath)
    print(f"Loaded {len(incidents)} incidents from {filepath}")

    # Full analysis
    analyze(incidents)

    # Filter examples (uncomment to use):
    # analyze(incidents, dept_filter="D team oven")
    # analyze(incidents, tenure_filter="< 1 month")
    # analyze(incidents, type_filter="loss")
