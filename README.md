<!-- academy:title -->
# الذكاء الاصطناعي في التنقل والخدمات اللوجستية

AI in Mobility and Logistics

مسار الطلاقة في البيانات والذكاء الاصطناعي · أكاديمية سدايا · USE-SEC-205 · المستوى 200

اختبر أدوات التخطيط والتنبؤ والسلامة في النقل قبل أن تثق بها: قواعد لا تعرفها أداة الحل، وخطوط أساس يجب أن يغلبها التنبؤ، ومعدلات حوادث لكل كيلومتر، وادعاءات أتمتة تُقرأ بمن يقود

يعمل المديرون الذين يخططون الشبكات ويديرون الأساطيل ويُسألون عن السلامة المرورية على مشغل لوجستي حضري افتراضي ببيانات رحلات عامة وبيانات اصطناعية للمعلوماتية عن بعد (telematics). ويقارنون خطة توصيل محسَّنة بخطة يدوية، ويختبرون تنبؤًا بالطلب في فترة العطلات، ويقرؤون بيانات الحوادث دون الوقوع في الفخاخ الإحصائية، ويضعون ادعاءات القيادة الآلية على مستويات الأتمتة، وينتهون بخريطة يدافعون عنها.

**الصيغة:** ورشة عمل: يومان من المختبرات، مع عمل تحضيري متعقَّب وخريطة تُناقَش

**صفحة المقرر:** https://sdaiaacademy.github.io/use-sec-205/
<!-- /academy:title -->

## نواتج التعلم

| | نواتج التعلم | المستوى | الدليل |
|---|---|---|---|
| LO1 | يصف مستويات أتمتة القيادة وما يعنيه كل ادعاء بالنسبة إلى السائق ونطاق التشغيل، استنادًا إلى ثمانية ادعاءات من الموردين والصحافة | Awareness | جدول صحيح في ستة صفوف |
| LO2 | يهيئ تشغيلًا لتخطيط المسارات يراعي النوافذ الزمنية والسعات، ويقارنه بخطة يدوية، على 120 عملية توصيل اصطناعية فوق بيانات خرائط مفتوحة | Applied | مقارنة للمسافة والتأخر تسمي القيود التي أغفلتها أداة الحل |
| LO3 | يختبر تنبؤًا بالطلب مقابل خطوط الأساس الموسمية الساذجة خلال فترة عطلة، باستخدام سجلات رحلات عامة وتنبؤ جاهز | Applied | جدول أخطاء وقاعدة للثقة |
| LO4 | يحلل حوادث الأسطول بمعدلات معدلة بحسب التعرض مع فحص للارتداد نحو المتوسط، على سنة اصطناعية لأسطول من 200 مركبة | Applied | مذكرة بالمعدلات لكل مليون كيلومتر |
| LO5 | يبني خريطة للفرص والمخاطر ترتب حالات استخدام التنقل بحسب القيمة وجاهزية البيانات وأثر السلامة ومستوى المخاطر، في المشغل الافتراضي ذي البيانات الاصطناعية | Performance | الخريطة، وتُناقَش أمام لجنة سلامة في جلسة محاكاة |

<!-- academy:units -->
## الوحدات

| الوحدة | العنوان | الجلسات | الشرائح |
|---|---|---|---|
| اليوم 1 | خطة على الطريق وتنبؤ بالموسم | أداة الحل لا تعرف ما يعرفه المرسِل; تنبؤ يجب أن يغلب الساذج | [`slides/day1.html`](slides/day1.html) |
| اليوم 2 | السلامة بأرقام صادقة، والأتمتة بكلمات دقيقة | المعدل قبل أي ادعاء سلامة; من يقود؟ ثم الخريطة | [`slides/day2.html`](slides/day2.html) |
| المناقشة الختامية | خريطة الفرص والمخاطر أمام لجنة السلامة |  | [`slides/capstone.html`](slides/capstone.html) |
<!-- /academy:units -->

## دراسة الحالة

المقرر كله يجري في جهة واحدة: **شركة رَكْب للخدمات اللوجستية الحضرية**، شركة افتراضية توصل الطرود والبقالة في الرياض
بمئتي مركبة في أربعة مستودعات. تنظر لجنة سلامتها في أربعة عروض: أداة حل لتخطيط المسارات، وتنبؤ «موسم» بالطلب،
وكاميرات «يَقِظ» لمراقبة السائق، ومركبات ذاتية القيادة في الساحة والأحياء. يجلس المشارك في مقعد أحد أعضاء اللجنة.

الطلبات الـ120 والأسطول وسنة حوادثه وحالات الاستخدام الأربع عشرة اصطناعية ومولَّدة ببذرة ثابتة، وفيها مشكلات مقصودة:
قواعد لا يعرفها نموذج أداة الحل (التبريد، والمساعد، ووقت الأبراج، وراحة السائق)، وتنبؤ بلا تقويم للعطلات، ومستودع هو
الأسوأ بالعدد والأفضل بالمعدل، وادعاء كاميرا يفسره الارتداد نحو المتوسط. المسافات من طرق حقيقية في
[OpenStreetMap](https://www.openstreetmap.org/copyright) (رخصة ODbL)، وسجلات الرحلات اليومية حقيقية من بوابة البيانات
المفتوحة لمدينة شيكاغو، وتنبؤ «موسم» اصطناعي. لا ملف يكشف بيانات شخص أو جهة حقيقية، ومفتاح الإجابات للمدرب في
`labs/solutions/`.

<!-- academy:labs -->
## المختبرات

كل مختبر صفحة في `labs/` تُفتح من صفحة المقرر ومن شريحة المختبر في جلسته.

| | الجلسة | المختبر | الملف |
|---|---|---|---|
| 1.1 | اليوم 1 · الجلسة 1 | أداة الحل مقابل خطة المرسِل | [`D1_1_routing.html`](labs/D1_1_routing.html) |
| 1.2 | اليوم 1 · الجلسة 2 | «موسم» في العطلات | [`D1_2_forecast.html`](labs/D1_2_forecast.html) |
| 2.1 | اليوم 2 · الجلسة 1 | حوادث رَكْب وادعاء «يَقِظ» | [`D2_1_incidents.html`](labs/D2_1_incidents.html) |
| 2.2 | اليوم 2 · الجلسة 2 | ثمانية ادعاءات، ثم الخريطة | [`D2_2_claims_and_map.html`](labs/D2_2_claims_and_map.html) |
<!-- /academy:labs -->

## المشروع الختامي

ثماني حالات استخدام مقيَّمة على الأقل ومشروع تجريبي واحد بحدود لبيانات السائقين، تُناقَش أمام لجنة سلامة في جلسة محاكاة.

**التسليم:** مشروع فردي يُسلَّم رابطًا لمجلد مشترك في Google Drive، فيه الخريطة بثماني حالات على الأقل (القيمة، وجاهزية
البيانات، وأثر السلامة، ومستوى المخاطر من مصفوفة الإطار الوطني، والدليل على كل درجة)، وورقة المشروع التجريبي الواحد
بمقياسه ومعايير إيقافه وحدود بيانات السائقين فيه (الغرض، وما لا يُجمع، ومدة الحفظ، ومن يرى)، ومخرجات المختبرات الأربعة.
كل حالة لها أثر سلامة، وكل مشروع تجريبي يمس السلامة، يسمّي دور التولي. ثم مناقشة: سبع دقائق للعرض وخمس للأسئلة، يعيد
فيها المشارك تقييم حالة تختارها اللجنة.

| المعيار | الوزن |
|---|---|
| اكتمال الخريطة: ثماني حالات على الأقل، ولكل درجة دليلها | 20 |
| سلامة التقييم: القيمة وجاهزية البيانات وأثر السلامة ومستوى المخاطر | 25 |
| حالات السلامة: دور تولٍّ مسمّى، وأرقام سلامة لكل كيلومتر | 20 |
| المشروع التجريبي: مقياس ومعايير إيقاف وحدود لبيانات السائقين | 20 |
| المناقشة: إعادة تقييم حالة تختارها اللجنة | 15 |

المعايير الأربعة الأولى (85 درجة) هي الخريطة، ووزنها 35% من التقييم؛ والمعيار الخامس (15 درجة) هو المناقشة، ووزنها 10%.
النجاح في الخريطة 60% منها، أي 51 درجة من 85 على الأقل.

## التقييم

فحص فردي بسيناريوهات دون ذكاء اصطناعي (20%)، ومخرجات المختبرات (35%)، والخريطة (35%)، والمناقشة أمام اللجنة (10%).
النجاح: 70% في المجموع و60% على الأقل في الخريطة، وكل مشروع تجريبي يمس السلامة يسمّي دور التولي. الذكاء الاصطناعي ممنوع
في الفحص وفي خطوات الادعاءات من المختبر 2.2، ومسموح بدور المعلّم في المختبرات الأخرى، ومسموح كاملًا في الخريطة التي
يدافع عنها المشارك حيًّا. مواد الفحص ليست في هذا المستودع.

أسئلة التدريب في `assessments/bank.json`، ومعها نقاط التحقق في الشرائح.

## العمل التحضيري

نحو ساعة قبل اليوم الأول، ويُتعقَّب تسليمه: يملأ المشارك بطاقة لقرار تخطيط أو سلامة واحد يتخذه أو يشارك فيه، وبياناته،
والقيد الذي يعرفه صاحب القرار ولا يظهر في أي ملف، دون أي بيان حقيقي عن سائق أو عميل. الدليل والبطاقة في
`labs/files/prework/`، وتُستخدم البطاقة في المختبر 1.1.

## المتطلبات السابقة

- USE-FLU-103 كيف تتعلم أنظمة الذكاء الاصطناعي وأين تخفق
- يعمل في النقل أو الخدمات اللوجستية أو يقدم المشورة فيهما

<!-- academy:tools -->
## الأدوات

كل سطر قدرة، والأمثلة قابلة للتبديل.

- **أداة حل لتخطيط مسارات المركبات:** OR-Tools, VROOM
- **بيانات الخرائط والنقل المفتوحة:** OpenStreetMap, بيانات عامة للرحلات والجداول الزمنية
- **التحليل دون برمجة:** جدول بيانات إلكتروني, Orange Data Mining, KNIME
<!-- /academy:tools -->

<!-- academy:sources -->
## المصادر

### المرجعيات الوطنية

- [نظام حماية البيانات الشخصية (سدايا)](https://sdaia.gov.sa/ar/SDAIA/about/Documents/PersonalDataProtectionLawAr.pdf)
- [مبادئ أخلاقيات الذكاء الاصطناعي (سدايا)](https://sdaia.gov.sa/ar/SDAIA/about/Documents/ai-principles.pdf)
- [الإطار الوطني لإدارة مخاطر الذكاء الاصطناعي، النص العربي (سدايا، أبريل 2026)](https://sdaia.gov.sa/ar/MediaCenter/KnowledgeCenter/ResearchLibrary/ExecutiveSummaryAr.pdf)

### الأتمتة والتنظيم

- [SAE International: SAE Levels of Driving Automation Refined for Clarity and International Audience (2021), with the J3016 visual chart](https://www.sae.org/news/blog/sae-levels-driving-automation-clarity-refinements)
- [SAE J3016_202609 (September 2026): Taxonomy and Definitions for Terms Related to Driving Automation Systems for On-Road Motor Vehicles, standard page and abstract](https://www.sae.org/standards/j3016_202609-taxonomy-definitions-terms-related-driving-automation-systems-road-motor-vehicles)
- [UK Automated Vehicles Act 2024, section 1: self-driving capability](https://www.legislation.gov.uk/ukpga/2024/10/section/1)
- [UK Automated Vehicles Act 2024, section 78: restriction of certain terms to authorised automated vehicles](https://www.legislation.gov.uk/ukpga/2024/10/section/78)

### التخطيط والتنبؤ والبيانات المفتوحة

- [Google OR-Tools: Vehicle Routing Problem with Time Windows](https://developers.google.com/optimization/routing/vrptw)
- [VROOM: Vehicle Routing Open-source Optimization Machine](https://github.com/VROOM-Project/vroom)
- [OpenStreetMap: copyright and licence (ODbL)](https://www.openstreetmap.org/copyright)
- [Project OSRM: open source routing machine on OpenStreetMap data](https://project-osrm.org/)
- [City of Chicago: Taxi Trips (2024-), open data portal](https://data.cityofchicago.org/Transportation/Taxi-Trips-2024-/ajtu-isnz)
- [City of Chicago: data disclaimer and terms of use](https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html)
- [Hyndman and Athanasopoulos, Forecasting: Principles and Practice (3rd ed.), Some simple forecasting methods](https://otexts.com/fpp3/simple-methods.html)
- [Hyndman and Athanasopoulos, Forecasting: Principles and Practice (3rd ed.), Evaluating point forecast accuracy](https://otexts.com/fpp3/accuracy.html)

### أدوات التحليل دون برمجة

- [Orange Data Mining](https://orangedatamining.com/)
- [KNIME Analytics Platform](https://www.knime.com/knime-analytics-platform)
<!-- /academy:sources -->

### المرجعيات الوطنية

- نظام حماية البيانات الشخصية: https://sdaia.gov.sa/ar/SDAIA/about/Documents/PersonalDataProtectionLawAr.pdf
- مبادئ أخلاقيات الذكاء الاصطناعي الصادرة عن سدايا: https://sdaia.gov.sa/ar/SDAIA/about/Documents/ai-principles.pdf
- الإطار الوطني لإدارة مخاطر الذكاء الاصطناعي: https://sdaia.gov.sa/ar/MediaCenter/KnowledgeCenter/ResearchLibrary/ExecutiveSummaryAr.pdf
