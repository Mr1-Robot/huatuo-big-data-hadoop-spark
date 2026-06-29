# NotebookLM Slide Brief

Use this document to generate a clean, minimal, 20-minute presentation based on the final report. The presentation should be technical, academic, and easy to present as a team. Do not create a marketing-style deck. Use simple layouts, clear section breaks, readable charts, and concise slide text.

Presentation title:

**Large-Scale Huatuo Medical QA Processing Using Hadoop Streaming and Apache Spark**

Design direction:

- Use a clean academic/technical style.
- Use white or very light backgrounds.
- Use dark text with muted blue, teal, or grey accents.
- Avoid heavy paragraphs.
- Use one dominant idea per slide.
- Use diagrams and charts from the report where relevant.
- Separate Hadoop case-study slides from Spark case-study slides so different team members can present them.
- Do not include a limitations slide.
- Keep the deck around 23 slides and approximately 20 minutes.

Suggested timing:

- Slides 1-9: dataset, integration, preprocessing, and case-study setup, around 8 minutes.
- Slides 10-14: Hadoop implementation, around 4.5 minutes.
- Slides 15-19: Spark implementation, around 4.5 minutes.
- Slides 20-23: benchmark results, output results, discussion, and conclusion, around 3 minutes.

Useful figure assets from the report folder:

- `figures/source_distribution.png`
- `figures/top_departments.png`
- `figures/answer_type_distribution.png`
- `figures/duplicate_records.png`
- `figures/pilot_execution_time.png`
- `figures/full_execution_time.png`
- `figures/full_total_time_share.png`
- `figures/full_spark_speedup.png`
- `figures/full_output_groups.png`
- `figures/dfd_case_study_1_department_demand.png`
- `figures/dfd_case_study_2_disease_symptom_trends.png`
- `figures/dfd_case_study_3_qa_quality.png`
- `figures/dfd_case_study_4_question_type.png`
- `figures/dfd_spark_case_study_1_department_demand.png`
- `figures/dfd_spark_case_study_2_disease_symptom_trends.png`
- `figures/dfd_spark_case_study_3_qa_quality.png`
- `figures/dfd_spark_case_study_4_question_type.png`

---

## Slide 1: Title

Title:

**Large-Scale Huatuo Medical QA Processing**

Subtitle:

**Comparative analytics using Hadoop Streaming and Apache Spark**

Content:

- Course: Big Data Processing
- Dataset: Huatuo medical question-answering sources
- Frameworks: Hadoop Streaming and Apache Spark
- Team member names

Visual:

- Clean title slide.
- Use a subtle data-pipeline visual motif, not a medical stock image.
- Mention the final scale: **34M+ records, 19GB unified JSONL**.

Speaker purpose:

Introduce the project as a complete big-data workflow, not only an analytics script.

---

## Slide 2: Problem and Motivation

Main message:

Medical QA datasets are valuable but difficult to analyze at scale because they come from multiple sources with different schemas, missing metadata, duplicate questions, URL answers, and mixed answer types.

Content:

- Medical QA data can support demand analysis, symptom trend mining, QA quality inspection, and question intent analysis.
- The raw sources are not immediately comparable because each source has different fields.
- A unified schema is needed before Hadoop and Spark can process the data fairly.

Visual:

- Simple flow: Multiple raw sources -> inconsistent fields -> unified processing -> analytics.

Speaker purpose:

Explain why preprocessing and unification are necessary before any framework comparison.

---

## Slide 3: Dataset Overview

Main message:

The project uses multiple Huatuo medical QA sources and combines them into one canonical dataset.

Content:

Source composition:

| Source | Records |
|---|---:|
| Consultation | 32,708,331 |
| Knowledge Graph | 798,444 |
| Encyclopedia | 364,420 |
| Lite | 177,703 |

Important scale values:

- Original source records: **34,048,913**
- Final unified records: **34,048,898**
- Original raw size: **5.432GB**
- Final canonical JSONL size: **20,168,846,076 bytes**, approximately **19GB**
- Excluded records: **15** records removed because the normalized question was unusable.

Visual:

- Use `figures/source_distribution.png`.

Speaker purpose:

Show that this is a large dataset and explain that the final file is larger because every row carries additional canonical fields.

---

## Slide 4: Why Union, Not Join

Main message:

Union was selected because the sources represent separate QA records, not shared entities with reliable join keys.

Content:

- A join requires a common key across datasets.
- These Huatuo sources do not share a stable patient ID, consultation ID, disease ID, or universal question ID.
- Joining would incorrectly remove or multiply records.
- Union keeps every valid QA record while preserving provenance through the `source` and `source_split` fields.
- After union, every record has the same canonical schema.

Visual:

- Left: wrong join idea showing unmatched keys.
- Right: correct union idea showing records stacked into one schema.

Speaker purpose:

Prepare a strong answer for the question: “Why did you combine the data using union instead of join?”

---

## Slide 5: Canonical Schema

Main message:

The unified dataset is based on a canonical JSONL schema designed for all four case studies.

Content:

Show a compact schema example:

```json
{
  "record_id": "source-specific-id",
  "source": "consultation",
  "source_split": "train",
  "question": "Normalized question text",
  "answer": "Normalized answer text or URL",
  "answer_type": "text | url | empty",
  "department": null,
  "related_disease": null,
  "quality_score": null,
  "metadata_origin": "observed | inferred | unavailable",
  "question_length": 25,
  "answer_length": 100,
  "question_hash": "sha256-value",
  "duplicate_flag": false
}
```

Key fields for case studies:

| Case study | Key fields |
|---|---|
| Department demand | `department`, `inferred_department`, `metadata_origin` |
| Disease/symptom trends | `question`, `answer`, `answer_type`, `related_disease` |
| QA quality | `source`, `answer_type`, `duplicate_flag`, `question_length`, `answer_length`, `quality_score` |
| Question type | `question` |

Visual:

- Use a clean schema table or code block.

Speaker purpose:

Show that the analytics are based on a deliberate schema, not ad hoc file reading.

---

## Slide 6: Preprocessing Pipeline

Main message:

The raw files were transformed into one validated canonical JSONL dataset before analytics.

Content:

Pipeline stages:

1. Load source JSON/JSONL records.
2. Normalize text fields.
3. Map source-specific fields into the canonical schema.
4. Classify answers as `text`, `url`, or `empty`.
5. Calculate question and answer lengths.
6. Generate `question_hash` using SHA-256.
7. Use the hash to set `duplicate_flag`.
8. Preserve provenance through `source` and `source_split`.
9. Write the unified JSONL file.

Explain normalization:

- Convert missing values to empty strings.
- Join list values into one string.
- Convert dictionary values to stable JSON text.
- Collapse repeated whitespace into a single space.
- Trim leading and trailing whitespace.

Visual:

- Pipeline diagram from raw sources to final unified JSONL.

Speaker purpose:

Show the data engineering work before Hadoop and Spark.

---

## Slide 7: Final Dataset Readiness

Main message:

The final dataset was validated and ready for Hadoop/Spark processing.

Content:

Final validation results:

- Final records: **34,048,898**
- Invalid JSON lines: **0**
- Missing questions: **0**
- Missing answers: **0**
- Duplicate questions: **10,162,575**, approximately **29.847%**
- URL answers: **32,708,326**
- Text answers: **1,340,572**
- Metadata observed: **177,703**
- Metadata unavailable: **33,871,195**

Visual:

- Use `figures/answer_type_distribution.png`.
- Use `figures/duplicate_records.png`.

Speaker purpose:

Show that the full data was inspected before running production jobs.

---

## Slide 8: Pilot Stage

Main message:

A deterministic pilot dataset was used to validate logic before processing the full 19GB file.

Content:

- Pilot size: **400,000 records**.
- Purpose: reduce risk before running the full dataset.
- Pilot confirmed that both Hadoop and Spark implementations produced matching output groups and aggregate values.
- The pilot also helped verify output structure, execution scripts, and result extraction.

Pilot benchmark:

| Case study | Hadoop pilot | Spark pilot |
|---|---:|---:|
| Department demand | 18.763s | 29.630s |
| Disease/symptom trends | 18.558s | 31.256s |
| QA quality | 19.602s | 25.309s |
| Question type | 18.560s | 23.310s |

Visual:

- Use `figures/pilot_execution_time.png`.

Speaker purpose:

Explain that the pilot was not the final result; it was a validation stage before full-scale execution.

---

## Slide 9: Case Study Overview

Main message:

The project evaluates four analytical questions over the same canonical dataset using both Hadoop and Spark.

Content:

| # | Case study | Analytical question | Grouping key |
|---|---|---|---|
| 1 | Department demand | Which departments appear most often? | Department + origin |
| 2 | Disease/symptom trends | Which disease and symptom terms appear most often? | Term type + term |
| 3 | QA quality | Which source has better completeness and quality? | Source |
| 4 | Question type | What kinds of questions do users ask? | Question type |

Speaker purpose:

Transition from data preparation to analytics implementation.

---

# Hadoop Section

## Slide 10: Hadoop Architecture

Main message:

Hadoop Streaming implements each case study using mapper output, Hadoop shuffle/sort, and reducer aggregation.

Content:

- Input: canonical JSONL file in HDFS.
- Mapper: reads one JSON record at a time and emits JSON key-value pairs.
- Shuffle/sort: groups identical keys.
- Reducer: sums counts or merges structured metrics.
- Output: JSON result groups.

Command pattern:

```bash
bash scripts/run_hadoop_streaming.sh CASE_STUDY HDFS_INPUT HDFS_OUTPUT
```

Visual:

- Architecture diagram: HDFS -> Mapper -> Shuffle/Sort -> Reducer -> HDFS output.

Speaker purpose:

Give the teammate a clear framework introduction before individual Hadoop case studies.

---

## Slide 11: Hadoop Case Study 1 - Department Demand

Main message:

Hadoop maps each record to a department key and reduces counts per department-origin pair.

Content:

Mapper logic:

- Read one canonical record.
- Use `department` if available.
- Otherwise use `inferred_department` if available.
- Emit key: `["department", department, origin]`.
- Emit value: `1`.

Reducer logic:

- Hadoop groups equal department keys.
- Reducer sums all values.
- Output: department count.

Code excerpt:

```python
def case_study_1(record):
    department = record.get("department") or record.get("inferred_department")
    if department:
        origin = "observed" if record.get("department") else "inferred"
        emit(["department", department, origin], 1)
```

Output result sample:

| Department | Count |
|---|---:|
| Obstetrics and Gynecology | 34,313 |
| Internal Medicine | 29,677 |
| Dermatology and Venereology | 24,668 |
| Pediatrics | 21,202 |
| ENT and Ophthalmology | 13,791 |

Visual:

- Use `figures/dfd_case_study_1_department_demand.png`.

Speaker purpose:

Explain map/reduce in the simplest case study.

---

## Slide 12: Hadoop Case Study 2 - Disease and Symptom Trends

Main message:

Hadoop performs rule-based medical term extraction and emits one key-value pair per matched term.

Content:

Mapper logic:

- Build searchable text from `question`.
- Add `answer` only if `answer_type == "text"`.
- Exclude URL answers from text matching.
- Match known disease and symptom terms from the rules file.
- Include observed `related_disease` metadata where available.
- Emit disease keys and symptom keys separately.

Reducer logic:

- Hadoop groups identical term keys.
- Reducer sums term frequency.

Code excerpt:

```python
def case_study_2(record, rules):
    text = record.get("question", "")
    if record.get("answer_type") == "text":
        text += " " + record.get("answer", "")
    observed_disease = record.get("related_disease") or record.get("inferred_disease")
    diseases = set(match_terms(text, rules.get("diseases", [])))
    if observed_disease:
        diseases.add(observed_disease)
    for disease in sorted(diseases):
        emit(["term", "disease", disease], 1)
    for symptom in match_terms(text, rules.get("symptoms", [])):
        emit(["term", "symptom", symptom], 1)
```

Output result sample:

| Type | Term | Count |
|---|---|---:|
| Symptom | Pain | 666,529 |
| Symptom | Cough | 567,381 |
| Symptom | Fever | 471,290 |
| Symptom | Headache | 193,634 |
| Disease | Vitiligo | 3,308 |
| Disease | Common cold | 2,371 |

Visual:

- Use `figures/dfd_case_study_2_disease_symptom_trends.png`.

Speaker purpose:

Defend that this is rule-based medical term extraction, not arbitrary word counting.

---

## Slide 13: Hadoop Case Study 3 - QA Quality and Completeness

Main message:

Hadoop computes structured quality metrics, not only counts.

Content:

Mapper logic:

- Emit one metrics object per record.
- Metrics include record count, empty question flag, empty answer flag, URL answer flag, duplicate flag, question length, answer length, score count, score sum, score min, and score max.

Reducer logic:

- Merge numeric sums.
- Preserve score minimum and maximum.
- Calculate average question length.
- Calculate average answer length.
- Calculate duplicate percentage.
- Calculate URL answer percentage.
- Calculate score average.

Code excerpt:

```python
def case_study_3(record):
    score = record.get("quality_score")
    emit(["source_quality", record.get("source", "unknown")], {
        "records": 1,
        "empty_questions": int(not record.get("question")),
        "empty_answers": int(record.get("answer_type") == "empty"),
        "url_answers": int(record.get("answer_type") == "url"),
        "duplicates": int(bool(record.get("duplicate_flag"))),
        "question_length_sum": int(record.get("question_length") or 0),
        "answer_length_sum": int(record.get("answer_length") or 0),
        "score_count": int(score is not None),
        "score_sum": float(score or 0),
        "score_min": score,
        "score_max": score,
    })
```

Output result:

| Source | Records | URL answers | Duplicates | Avg answer length |
|---|---:|---:|---:|---:|
| Consultation | 32,708,331 | 32,708,326 | 10,025,707 | 0.000003 |
| Encyclopedia | 364,420 | 0 | 134,305 | 540.4753 |
| Knowledge Graph | 798,444 | 0 | 1,023 | 35.8706 |
| Lite | 177,703 | 0 | 1,540 | 143.8183 |

Visual:

- Use `figures/dfd_case_study_3_qa_quality.png`.

Speaker purpose:

This is the best slide to answer criticism that the case studies are simple counting.

---

## Slide 14: Hadoop Case Study 4 - Question-Type Distribution

Main message:

Hadoop classifies each question into a deterministic intent category and counts categories.

Content:

Question types:

- Cause
- Diagnosis
- Medication
- Prevention
- Symptom
- Treatment
- Other

Mapper logic:

- Read normalized question.
- Match against rule-based keyword groups.
- Use the first matching category in sorted order.
- Emit `["question_type", question_type]` with value `1`.

Reducer logic:

- Group by question type.
- Sum category counts.

Code excerpt:

```python
def classify_question(question, patterns):
    matches = [
        category
        for category, terms in sorted(patterns.items())
        if match_terms(question, terms)
    ]
    return matches[0] if matches else "other"

def case_study_4(record, rules):
    question_type = classify_question(
        record.get("question", ""), rules.get("question_types", {})
    )
    emit(["question_type", question_type], 1)
```

Output result:

| Question type | Count |
|---|---:|
| Other | 24,580,705 |
| Treatment | 3,811,062 |
| Medication | 2,275,619 |
| Cause | 1,526,071 |
| Diagnosis | 1,000,666 |
| Symptom | 735,580 |
| Prevention | 119,195 |

Visual:

- Use `figures/dfd_case_study_4_question_type.png`.

Speaker purpose:

Explain the rule-based classification approach and show the final distribution.

---

# Spark Section

## Slide 15: Spark Architecture

Main message:

Spark implements the same analytics using DataFrame transformations, UDFs, groupBy aggregations, and JSON output.

Content:

- Input: same canonical JSONL file.
- Spark reads data using `spark.read.json`.
- Transformations include `select`, `withColumn`, UDFs, `explode`, `unionByName`, `groupBy`, and `agg`.
- Output: JSON result groups.

Command pattern:

```bash
bash scripts/run_spark.sh CASE_STUDY INPUT_JSONL OUTPUT_PATH
```

Visual:

- Architecture diagram: JSONL -> Spark DataFrame -> Transform/UDF -> Aggregate -> JSON output.

Speaker purpose:

Introduce Spark’s programming model before individual Spark case studies.

---

## Slide 16: Spark Case Study 1 - Department Demand

Main message:

Spark resolves observed and inferred department rows, unions them, and groups by department and origin.

Content:

Spark logic:

- Select rows where `department` or `inferred_department` exists.
- Assign origin as `observed` or `inferred`.
- Infer departments from question text only when rule mappings exist.
- Union observed and inferred rows.
- Group by `department` and `origin`.
- Count and order results.

Code excerpt:

```python
observed = (
    df.where(F.coalesce("department", "inferred_department").isNotNull())
    .select(
        F.coalesce("department", "inferred_department").alias("department"),
        F.when(F.col("department").isNotNull(), "observed")
         .otherwise("inferred").alias("origin"),
    )
)

return (
    observed.unionByName(inferred)
    .groupBy("department", "origin")
    .count()
    .orderBy(F.desc("count"), "department")
)
```

Output result:

- Same 16 department groups as Hadoop.
- Top department: Obstetrics and Gynecology, 34,313 records.

Visual:

- Use `figures/dfd_spark_case_study_1_department_demand.png`.

Speaker purpose:

Show the Spark DataFrame equivalent of Hadoop map/reduce logic.

---

## Slide 17: Spark Case Study 2 - Disease and Symptom Trends

Main message:

Spark uses UDFs to create arrays of matched terms, explodes them into rows, and groups by term.

Content:

Spark logic:

- UDF matches symptom terms.
- UDF matches disease terms.
- Text uses question and text answer only.
- URL answers are excluded from answer text.
- `explode` creates one row per matched term.
- Disease rows and symptom rows are unioned.
- Group by `term_type` and `term`.

Code excerpt:

```python
diseases = (
    df.withColumn(
        "matched_diseases",
        disease_udf(
            "question",
            "answer",
            "answer_type",
            F.coalesce("related_disease", "inferred_disease"),
        ),
    )
    .select(F.explode("matched_diseases").alias("term"))
    .withColumn("term_type", F.lit("disease"))
)

return (
    diseases.unionByName(symptoms)
    .groupBy("term_type", "term")
    .count()
    .orderBy(F.desc("count"), "term")
)
```

Output result:

- Same 2,711 term groups as Hadoop.
- Most frequent symptom term: Pain, 666,529.

Visual:

- Use `figures/dfd_spark_case_study_2_disease_symptom_trends.png`.

Speaker purpose:

Explain that Spark’s `explode` replaces Hadoop’s multiple mapper emits.

---

## Slide 18: Spark Case Study 3 - QA Quality and Completeness

Main message:

Spark computes source-level quality metrics using grouped DataFrame aggregations.

Content:

Spark logic:

- Group records by `source`.
- Count records.
- Sum empty question flags.
- Sum empty answer flags.
- Sum URL answers.
- Sum duplicate flags.
- Average question length.
- Average answer length.
- Average, min, and max quality score.
- Add duplicate and URL answer percentages.

Code excerpt:

```python
return (
    df.groupBy("source")
    .agg(
        F.count("*").alias("records"),
        F.sum((F.col("answer_type") == "url").cast("int")).alias("url_answers"),
        F.sum(F.col("duplicate_flag").cast("int")).alias("duplicates"),
        F.avg("question_length").alias("average_question_length"),
        F.avg("answer_length").alias("average_answer_length"),
        F.avg(score).alias("score_average"),
        F.min(score).alias("score_min"),
        F.max(score).alias("score_max"),
    )
    .withColumn("duplicate_percentage", 100 * F.col("duplicates") / F.col("records"))
    .withColumn("url_answer_percentage", 100 * F.col("url_answers") / F.col("records"))
)
```

Output result:

- Same 4 source-quality groups as Hadoop.
- Consultation has almost all URL answers.
- Lite has observed quality scores with average around 4.1281.

Visual:

- Use `figures/dfd_spark_case_study_3_qa_quality.png`.

Speaker purpose:

Show why Spark was faster for this case study: grouped aggregations are well suited to DataFrame execution.

---

## Slide 19: Spark Case Study 4 - Question-Type Distribution

Main message:

Spark applies a rule-based classifier as a UDF, then groups and counts question types.

Content:

Spark logic:

- Load question-type keyword patterns from rules.
- UDF scans normalized question text.
- Assign first matching category.
- Assign `other` if no rule matches.
- Group by `question_type`.
- Count and order results.

Code excerpt:

```python
def classify(question):
    folded = (question or "").casefold()
    for category in sorted(patterns):
        if any(term.casefold() in folded for term in patterns[category]):
            return category
    return "other"

classify_udf = F.udf(classify, T.StringType())
return (
    df.withColumn("question_type", classify_udf("question"))
    .groupBy("question_type")
    .count()
    .orderBy(F.desc("count"), "question_type")
)
```

Output result:

- Same 7 question-type groups as Hadoop.
- Largest category: Other, 24,580,705.
- Largest recognized category: Treatment, 3,811,062.

Visual:

- Use `figures/dfd_spark_case_study_4_question_type.png`.

Speaker purpose:

Show Spark’s classification workflow and connect it to the same analytical result as Hadoop.

---

# Results Section

## Slide 20: Full Benchmark Results

Main message:

Spark was faster overall on the full 19GB unified dataset, while Hadoop remained competitive for simpler streaming-style workloads.

Content:

Full benchmark:

| Case study | Hadoop | Spark | Faster framework |
|---|---:|---:|---|
| Department demand | 128.071s | 117.327s | Spark |
| Disease/symptom trends | 139.457s | 149.503s | Hadoop |
| QA quality | 273.549s | 82.296s | Spark |
| Question type | 204.027s | 113.497s | Spark |
| Total | 745.104s | 462.623s | Spark |

Key interpretation:

- Spark total improvement was approximately **37.9%**.
- Hadoop was slightly faster for disease/symptom trend extraction.
- Spark was much faster for QA quality because grouped aggregations fit Spark well.

Visual:

- Use `figures/full_execution_time.png`.
- Optionally include `figures/full_spark_speedup.png`.

Speaker purpose:

Present the main benchmark comparison.

---

## Slide 21: Output Results and Analytical Findings

Main message:

Both frameworks produced matching output group counts and equivalent aggregate results.

Content:

Output groups:

| Case study | Output groups |
|---|---:|
| Department demand | 16 |
| Disease/symptom trends | 2,711 |
| QA quality | 4 |
| Question type | 7 |

Analytical findings:

- Consultation records dominate the dataset.
- Consultation answers are mostly URLs.
- Top observed department: Obstetrics and Gynecology.
- Top symptom terms: Pain, cough, fever, and headache.
- Largest recognized question type: Treatment.
- QA quality analysis exposes source-level differences in answer length, duplicates, URL answer rate, and score availability.

Visual:

- Use `figures/full_output_groups.png`.
- Use selected small table or chart from outputs.

Speaker purpose:

Show that the implementation produced meaningful output, not just execution times.

---

## Slide 22: Discussion - Why This Is More Than Counting Words

Main message:

The project includes data integration, schema design, validation, rule-based extraction, classification, structured metrics, and framework benchmarking.

Content:

Defensive points:

- The dataset was not used raw; it was standardized into a canonical schema.
- Duplicates were detected through SHA-256 question hashing.
- Answer types were classified as text, URL, or empty.
- Disease and symptom trends used controlled medical term rules.
- Question-type distribution used rule-based classification.
- QA quality used structured metrics, averages, percentages, min/max scores, and duplicate rates.
- Hadoop and Spark were implemented separately but validated against the same outputs.

Recommended phrase:

“Some case studies use counts as the final aggregation, but the work before the count is the important big-data processing step: schema unification, text normalization, feature creation, term extraction, classification, and quality metric computation.”

Visual:

- Use a split slide:
  - Left: “Not just counting”
  - Right: “Processing techniques used”

Speaker purpose:

Prepare a direct answer to the lecturer’s criticism.

---

## Slide 23: Conclusion

Main message:

The project successfully transformed multiple Huatuo medical QA sources into a large unified dataset and compared Hadoop and Spark across four healthcare analytics case studies.

Content:

Final contribution:

- Unified multiple Huatuo medical QA sources into one canonical JSONL dataset.
- Produced a validated **34,048,898-record**, approximately **19GB** dataset.
- Implemented four healthcare analytics case studies in Hadoop Streaming.
- Implemented equivalent case studies in Apache Spark.
- Verified matching output groups and aggregate results.
- Benchmarked both frameworks on the full unified dataset.
- Found Spark faster overall, while Hadoop remained competitive for simpler streaming extraction.

Closing line:

“The main outcome is a reproducible big-data pipeline that turns heterogeneous medical QA sources into a unified dataset and comparable Hadoop/Spark analytics outputs.”

Visual:

- Simple final pipeline: Raw Huatuo sources -> Canonical dataset -> Hadoop/Spark analytics -> Results.

Speaker purpose:

End with the project contribution and avoid adding new weaknesses at the end.

