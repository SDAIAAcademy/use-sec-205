# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["ortools==9.14.6206", "openpyxl==3.1.5"]
# ///
"""Writes the Rakb Urban Logistics file pack of USE-SEC-205 into labs/files/, with a fixed seed.
The road matrices (files/routing/distance_m.csv, duration_s.csv, snapped_points.csv) come from
fetch_matrix.py and are read, not rewritten. Usage: uv run labs/_tools/prepare_files.py"""
import csv
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LABS = HERE.parent
FILES = LABS / "files"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(FILES / "routing"))

from openpyxl import Workbook  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

import gen_forecast  # noqa: E402
import gen_incidents  # noqa: E402
import gen_routing  # noqa: E402
import rakb_routing  # noqa: E402
import texts as T  # noqa: E402

FILL = PatternFill("solid", fgColor="FFF2CC")
HEAD = Font(bold=True)


def text(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8", newline="\n")


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def xlsx(path, sheets):
    """sheets: list of (title, header, rows, fill_columns, widths)."""
    wb = Workbook()
    wb.remove(wb.active)
    for title, header, rows, fill, widths in sheets:
        ws = wb.create_sheet(title)
        ws.sheet_view.rightToLeft = True
        ws.append(header)
        for c in ws[1]:
            c.font = HEAD
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for r in rows:
            ws.append(r)
        for col in fill:
            for row in range(1, ws.max_row + 1):
                ws.cell(row=row, column=col).fill = FILL
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
        ws.freeze_panes = "A2"
    wb.properties.creator = "SDAIA Academy USE-SEC-205"
    wb.save(path)


def routing():
    d = FILES / "routing"
    with open(d / "snapped_points.csv", encoding="utf-8") as f:
        snapped = [(r["id"], float(r["lat"]), float(r["lon"])) for r in csv.DictReader(f)]
    rows = gen_routing.deliveries(snapped)
    fields = ["id", "lat", "lon", "crates", "win_start", "win_end", "cold", "lift", "tower", "kind"]
    write_csv(d / "deliveries_120.csv", rows, fields)
    write_csv(d / "fleet.csv", gen_routing.FLEET, ["id", "capacity", "kind"])
    xlsx(d / "deliveries_120.xlsx", [("الطلبات", fields, [[r[k] for k in fields] for r in rows], [], [8, 10, 10, 8, 10, 10, 6, 6, 6, 22])])
    case = rakb_routing.load(d)
    manual = gen_routing.manual_plan(case["stops"], case)
    rakb_routing.write_plan(d / "manual_plan.csv", manual)
    solver = rakb_routing.solve(case, ())
    rakb_routing.write_plan(d / "solver_plan_reference.csv", solver)
    m_rows, _ = rakb_routing.replay(case, manual)
    xlsx(d / "manual_plan.xlsx", [("خطة عايد", ["van", "seq", "stop"], [[r["van"], r["seq"], r["stop"]] for r in m_rows], [], [8, 6, 8])])
    header = ["المقياس", "خطة عايد اليدوية", "أداة الحل: التشغيل الأول", "أداة الحل: بعد إضافة القواعد", "ملاحظتك"]
    measures = ["الشاحنات المستخدمة", "الكيلومترات", "الطلبات المتأخرة", "دقائق التأخر", "شاحنات تعود بعد الدقيقة 480",
                "بقالة مبرّدة في شاحنة غير مبرّدة", "أثاث في شاحنة بلا مساعد"]
    xlsx(d / "comparison_sheet.xlsx", [
        ("المقارنة", header, [[m, None, None, None, None] for m in measures], [2, 3, 4, 5], [34, 18, 22, 24, 40]),
        ("القيود التي أغفلتها الأداة", ["القيد", "أين وجدته", "كم طلبًا أو شاحنة مسّ", "هل يمكن إعطاؤه لأداة الحل؟ كيف؟"],
         [[None] * 4 for _ in range(5)], [1, 2, 3, 4], [30, 24, 18, 40]),
    ])
    text(d / "dispatcher_notes.txt", T.DISPATCHER_NOTES)
    text(d / "README.txt", T.ROUTING_README)
    text(d / "ATTRIBUTION.txt", T.ROUTING_ATTRIBUTION)
    return case, manual, solver


def forecast():
    d = FILES / "forecast"
    rows = gen_forecast.table()
    fields = ["date", "weekday", "trips", "mawsim_forecast", "period", "holiday"]
    write_csv(d / "trips_daily.csv", rows, fields)
    header = fields + ["lag7", "lag364", "err_mawsim", "err_lag7", "err_lag364", "abs_mawsim", "abs_lag7", "abs_lag364"]
    xlsx(d / "trips_daily.xlsx", [
        ("الرحلات", header, [[r[k] for k in fields] + [None] * 8 for r in rows], [7, 8, 9, 10, 11, 12, 13, 14], [12, 10, 9, 14, 8, 16, 9, 9, 11, 11, 11, 11, 11, 11]),
        ("جدول الأخطاء", ["الطريقة", "MAE عادية", "MAPE عادية", "MAE عطلات", "MAPE عطلات"],
         [["موسم", None, None, None, None], ["الأسبوع الماضي (lag7)", None, None, None, None], ["العام الماضي (lag364)", None, None, None, None]],
         [2, 3, 4, 5], [24, 12, 12, 12, 12]),
        ("قاعدة الثقة", ["متى نثق بتنبؤ «موسم»؟", "ومتى نستخدم خط الأساس؟", "ما الذي نطلبه من المورِّد؟"], [[None] * 3], [1, 2, 3], [40, 40, 40]),
    ])
    text(d / "mawsim_brochure.txt", T.MAWSIM_BROCHURE)
    text(d / "ATTRIBUTION.txt", T.FORECAST_ATTRIBUTION)
    return rows


def incidents():
    d = FILES / "incidents"
    table, equipped, comparison, ranked = gen_incidents.year()
    fields = ["vehicle", "depot", "type", "month", "km", "incidents", "camera"]
    write_csv(d / "fleet_year_2025.csv", table, fields)
    xlsx(d / "fleet_year_2025.xlsx", [("الأسطول", fields, [[r[k] for k in fields] for r in table], [], [9, 10, 14, 10, 9, 9, 8])])
    s = gen_incidents.summary(table, equipped, comparison)
    eq = s["equipped"]
    claim = f"""«يَقِظ لكاميرات الأساطيل» · رسالة إلى إدارة رَكْب · مورِّد افتراضي

في بداية أبريل 2025 ركّبنا كاميرات «يَقِظ» لمراقبة السائق في عشرين مركبة: المركبات العشرون التي سجّلت أكثر الحوادث في الربع الأول (يناير إلى مارس).
النتيجة: انخفضت حوادث هذه المركبات من {eq['q1']} حادثًا في الربع الأول إلى {eq['q2']} في الربع الثاني (أبريل إلى يونيو)، أي بنسبة {abs(eq['change_pct'])}%.
نقترح تركيب الكاميرات في الأسطول كله (200 مركبة)، مع حفظ المقاطع سنة كاملة لأغراض التدريب.

المركبات المجهزة: العمود camera = 1 من أبريل في fleet_year_2025.csv.
"""
    text(d / "yaqiz_claim.txt", claim)
    text(d / "note_template.txt", T.NOTE_TEMPLATE)
    text(d / "README.txt", T.INCIDENTS_README)
    return s, equipped, comparison


def claims():
    d = FILES / "claims"
    text(d / "claims_8.txt", T.CLAIMS_8)
    text(d / "levels_card.txt", T.LEVELS_CARD)
    header = ["الادعاء", "المستوى (0 إلى 5)", "من يقود حين تعمل الخاصية؟", "هل يجب على الإنسان أن يشرف؟", "نطاق التشغيل كما ورد",
              "هل يُطلب من الإنسان أن يتولى؟ متى؟", "ما الدليل الذي تطلبه قبل أن تصدّق؟"]
    xlsx(d / "claims_table.xlsx", [("الادعاءات", header, [[f"C{k}"] + [None] * 6 for k in range(1, 9)], [2, 3, 4, 5, 6, 7], [8, 12, 18, 16, 26, 26, 34])])


def map_pack():
    d = FILES / "map"
    text(d / "scoring_scale.txt", T.SCORING_SCALE)
    text(d / "pilot_sheet.txt", T.PILOT_SHEET)
    text(d / "README.txt", T.MAP_README)
    cards = ["أربع عشرة حالة استخدام معروضة على لجنة السلامة في رَكْب · كلها افتراضية\n"]
    for uid, title, does, value, data, safety, lab in T.USE_CASES:
        block = f"\n{uid} · {title}\nما تفعله: {does}\nالقيمة: {value}\nالبيانات: {data}\nأثر السلامة: {safety}\n"
        if lab:
            block += lab + "\n"
        cards.append(block)
    text(d / "use_cases_14.txt", "".join(cards))
    header = ["الحالة", "الاسم", "القيمة (1 إلى 5)", "جاهزية البيانات (1 إلى 5)", "القيمة × الجاهزية", "أثر السلامة", "الاحتمالية (1 إلى 4)",
              "الأثر (1 إلى 4)", "مستوى المخاطر", "دور التولي", "حدود بيانات السائقين", "الدليل على الدرجات"]
    xlsx(d / "map_template.xlsx", [("الخريطة", header, [[None] * 12 for _ in range(14)], list(range(1, 13)), [8, 26, 10, 12, 10, 12, 10, 10, 12, 26, 30, 34])])


def prework():
    d = FILES / "prework"
    text(d / "prework_guide.txt", T.PREWORK_GUIDE)
    text(d / "rakb_profile.txt", T.RAKB_PROFILE)
    qs = ["ما القرار، ومن يتخذه، وكم مرة؟", "ما البيانات المستخدمة اليوم، وأين تُحفظ، ومن يملكها؟", "ما الذي يُقاس بعد القرار؟",
          "ما القيد الذي يعرفه صاحب القرار ولا يظهر في أي ملف؟", "أي خطأ من أداة يضر الناس أو الطريق، وأيه يضر الميزانية فقط؟",
          "هل في البيانات موقع شخص أو سلوكه؟ لأي غرض جُمع، وكم يُحفظ؟"]
    xlsx(d / "decision_card.xlsx", [("بطاقة القرار", ["السؤال", "جوابك"], [[q, None] for q in qs], [2], [52, 70])])


def main():
    case, manual, solver = routing()
    rows = forecast()
    s, _, _ = incidents()
    claims()
    map_pack()
    prework()
    print("routing manual", rakb_routing.replay(case, manual)[1])
    print("routing solver", rakb_routing.replay(case, solver)[1])
    print("forecast", gen_forecast.errors(rows))
    print("incidents", s)


if __name__ == "__main__":
    main()
