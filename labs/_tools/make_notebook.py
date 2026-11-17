# /// script
# requires-python = ">=3.11"
# ///
"""Writes labs/files/routing/routing_lab.ipynb, the provided notebook of lab 1.1.
Participants run its cells and change the switches; they write no code."""
import json
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "files" / "routing" / "routing_lab.ipynb"
SITE = "https://sdaiaacademy.github.io/use-sec-205/labs/files/routing/"
FILES = ["rakb_routing.py", "deliveries_120.csv", "fleet.csv", "distance_m.csv", "duration_s.csv",
         "manual_plan.csv", "solver_plan_reference.csv"]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


cells = [
    md("""
# المختبر 1.1 · أداة الحل مقابل خطة المرسِل

شركة رَكْب للخدمات اللوجستية الحضرية (افتراضية). 120 طلبًا اصطناعيًا على طرق الرياض من OpenStreetMap، وثماني شاحنات صغيرة.

**لا تكتب كودًا.** شغّل كل خلية بالترتيب (Shift + Enter)، واقرأ ما تطبعه، وانقل الأرقام إلى `comparison_sheet.xlsx`. في الخلية 5 تغيّر مفاتيح من `False` إلى `True`، لا أكثر.

الأوقات بالدقائق من بداية الوردية (480 دقيقة). المسافات على الطرق الفعلية، والأزمنة بلا ازدحام.
"""),
    md("## 1 · التجهيز\nتثبّت الخلية أداة الحل (OR-Tools) إن لم تكن مثبتة، وتقرأ ملفات المختبر من المجلد نفسه إن وُجدت، وإلا نزّلتها من موقع المقرر."),
    code(f"""
import os, sys, pathlib, subprocess, urllib.request

SITE = "{SITE}"
FILES = {FILES!r}
try:
    import ortools  # noqa: F401
except ImportError:  # Colab and most fresh environments: install the solver once
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "ortools==9.14.6206"], check=True)

here = pathlib.Path.cwd()
if not (here / "deliveries_120.csv").exists():
    here = pathlib.Path("rakb_routing_files")
    here.mkdir(exist_ok=True)
    try:
        for name in FILES:
            if not (here / name).exists():
                urllib.request.urlretrieve(SITE + name, here / name)
    except Exception as e:
        raise SystemExit("تعذّر تنزيل ملفات المختبر (" + str(e) + "). ارفع ملفات مجلد routing بجانب الدفتر ثم شغّل الخلية من جديد.")
sys.path.insert(0, str(here))
import rakb_routing as R
case = R.load(here)
FULL_FLEET = list(case["fleet"])
print("طلبات:", len(case["stops"]), "| شاحنات:", len(case["fleet"]), "| صناديق:", sum(s["crates"] for s in case["stops"]))
"""),
    md("## 2 · خطة عايد اليدوية، بقواعده الأربع\nنعيد «قيادة» الخطة: كل شاحنة تخرج في الدقيقة 0، وتنتظر إن وصلت قبل النافذة، وتأخذ راحتها، وتعود."),
    code("""
manual = R.read_plan(here / "manual_plan.csv")
manual_rows, manual_sum = R.replay(case, manual)
manual_sum
"""),
    md("## 3 · التشغيل الأول لأداة الحل\nالنموذج يعرف: السعات، ونوافذ التسليم، و5 دقائق لكل تسليم. ولا يعرف شيئًا آخر. التشغيل يأخذ ثواني."),
    code("""
try:
    solver_plan = R.solve(case, rules=())
except Exception as e:  # إن تعذّر تشغيل أداة الحل، نبدأ من خطتها المحفوظة
    print("لم تعمل أداة الحل هنا:", e, "| نستخدم solver_plan_reference.csv")
    solver_plan = R.read_plan(here / "solver_plan_reference.csv")
print("كما تراها أداة الحل:", R.replay(case, solver_plan, rules=())[1])
"""),
    md("## 4 · الخطة نفسها بقواعد عايد\nالخطة لم تتغير. تغيّرت القواعد التي نحكم بها عليها. انقل الأرقام إلى العمود الثاني من جدول المقارنة، واقرأ قائمة المخالفات."),
    code("""
solver_rows, solver_sum = R.replay(case, solver_plan)
print(solver_sum)
for r in solver_rows:
    if r["breach"] or r["late_min"]:
        print(r["van"], r["stop"], "| مخالفة:", r["breach"] or "-", "| تأخر بالدقائق:", r["late_min"])
"""),
    md("""
## 5 · أعطِ أداة الحل ما يعرفه عايد
غيّر المفاتيح التي تراها مناسبة إلى `True`، ثم شغّل الخلية. القاعدة الرابعة (الراحة) لا تعرفها هذه النسخة من النموذج: ستراها في إعادة القيادة فقط.
"""),
    code("""
ADD_COLD = False      # البقالة المبرّدة على V8 فقط
ADD_LIFT = False      # الأثاث على V2 فقط
ADD_SERVICE = False   # 15 دقيقة في الأبراج
VANS = 8              # ✱ إضافي: جرّب 7

case["fleet"] = FULL_FLEET[:VANS]

rules = [name for name, on in (("cold", ADD_COLD), ("lift", ADD_LIFT), ("service", ADD_SERVICE)) if on]
plan2 = R.solve(case, rules=rules)
rows2, sum2 = R.replay(case, plan2)
print("القواعد في النموذج:", rules)
print(sum2)
for r in rows2:
    if r["breach"] or r["late_min"]:
        print(r["van"], r["stop"], "| مخالفة:", r["breach"] or "-", "| تأخر بالدقائق:", r["late_min"], "| راحة بعدها:", r["rest_after"] or "-")
"""),
    md("## 6 · المقارنة في جدول واحد"),
    code("""
names = ["خطة عايد", "الأداة: التشغيل الأول", "الأداة: بعد القواعد"]
for key in ("km", "late_stops", "late_minutes", "vans_overtime", "cold_breaches", "lift_breaches"):
    print(f"{key:15}", *[f"{s[key]:>10}" for s in (manual_sum, solver_sum, sum2)])
R.write_plan("my_solver_plan.csv", plan2)
print("حُفظت خطتك في my_solver_plan.csv")
"""),
    md("""
## ✱ إضافي
عُد إلى الخلية 5 واجعل `VANS = 7`، ثم شغّلها. هل تكفي سبع شاحنات؟ ما الذي ستقوله لمازن الشعيل عن الشاحنة الثامنة؟
"""),
]

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                   "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
for i, c in enumerate(nb["cells"]):
    c["id"] = f"cell-{i + 1}"
OUT.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("wrote", OUT.name)
