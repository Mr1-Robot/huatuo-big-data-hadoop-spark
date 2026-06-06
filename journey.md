# Huatuo Big Data Project Journey

## 1. Project Goal

This project is an Alternative Assessment for the WOC7017 Big Data Processing
course.

The assessment requires:

- A healthcare problem that requires big-data processing.
- A dataset larger than 2 GB.
- Several MapReduce algorithms or case studies.
- Equivalent implementations using Hadoop and Apache Spark.
- Processing-time comparison between Hadoop and Spark.
- Discussion of the complete data analytics lifecycle.

Our selected project is:

> Big Data Processing and Comparative Analytics for Large-Scale Medical
> Knowledge Discovery in the Huatuo-26M Dataset

## 2. Verified Dataset Sources

We downloaded the original published Hugging Face repository files without
converting or rewriting them.

| Source             | Main fields                                                      |        Records |         Size |
| ------------------ | ---------------------------------------------------------------- | -------------: | -----------: |
| Consultation QA    | `questions`, `answers`                                           |     32,708,346 |     4.537 GB |
| Encyclopedia QA    | `questions`, `answers`                                           |        364,420 |     0.608 GB |
| Knowledge Graph QA | `questions`, `answers`                                           |        798,444 |     0.149 GB |
| Huatuo26M-Lite     | `id`, `question`, `answer`, `score`, `label`, `related_diseases` |        177,703 |     0.138 GB |
| **Combined**       | Heterogeneous medical QA records                                 | **34,048,913** | **5.432 GB** |

The combined original source size is:

```text
5,431,518,498 bytes
5.432 decimal GB
5.058 GiB
```

This satisfies the assessment requirement for a dataset larger than 2 GB.

## 3. Important Dataset Findings

### Consultation QA

The consultation source contains patient questions, but its answers are mainly
URLs rather than answer text.

```json
{
  "questions": ["Patient question"],
  "answers": ["https://example-medical-site/question/123"]
}
```

### Encyclopedia and Knowledge Graph QA

These sources contain questions and textual answers:

```json
{
  "questions": ["Medical question"],
  "answers": ["Medical answer text"]
}
```

Some fields contain nested lists, so they must be normalized before analysis.

### Huatuo26M-Lite

Lite contains the richest metadata:

```json
{
  "id": 22647835,
  "question": "Medical question",
  "answer": "Medical answer",
  "score": 5,
  "label": "眼耳鼻喉科",
  "related_diseases": "鼻中隔偏曲"
}
```

## 4. Selected Case Studies

The selected case studies use available dataset fields and transparently
distinguish observed metadata from inferred metadata.

### Case Study 1: Medical Department Demand

Count observed department labels from Lite. Optional inferred department results
must be reported separately.

Techniques:

- Filtering
- Grouping
- Counting
- Sorting
- Top-N retrieval

### Case Study 2: Disease and Symptom Trend Mining

Count disease and symptom mentions across medical questions and textual answers.

Techniques:

- WordCount
- Pattern matching
- Grouping
- Counting
- Sorting

### Case Study 3: Medical QA Quality and Completeness

Compare source-level quality characteristics such as:

- Missing answers
- URL-only answers
- Duplicate questions
- Average question and answer lengths
- Lite quality scores

Techniques:

- Partitioning
- Filtering
- Average calculation
- Min/max retrieval
- Percentage calculation

### Case Study 4: Question-Type and Framework Performance

Classify medical questions into types such as symptoms, causes, diagnosis,
treatment, medication, and prevention. Run the same task in Hadoop and Spark to
compare processing time.

Techniques:

- Pattern matching
- Classification
- Grouping
- Counting
- Processing-time calculation

## 5. Data Integration Decision

The four datasets must be **unioned**, not joined.

A join would imply that records from different sources describe the same
consultation or patient. No reliable shared identifier exists to support that
claim.

The unification is therefore based on shared semantic structure rather than
shared IDs. All selected sources contain medical question-answer records, so
their available fields can be mapped into one canonical QA schema. The original
source identity is preserved in the `source` and `source_split` fields.

This avoids creating false relationships between records. For example, a
consultation record and an encyclopedia record may both discuss the same disease,
but that does not prove they describe the same patient, question, or medical
event. A union keeps them as separate observations in one integrated analytical
dataset.

Presentation justification:

> The Huatuo sources were unified by schema normalization and union. We did not
> join records because there is no trustworthy shared key across all sources.
> Instead, each medical QA record was converted into the same canonical schema,
> source provenance was preserved, unavailable metadata was represented as null,
> and duplicate questions were flagged transparently using a normalized question
> hash.

The planned integration flow is:

```text
Original Huatuo source JSONL files
                |
                v
Normalize different source schemas
                |
                v
Create one canonical JSONL schema
                |
                v
Union all standardized records
                |
                v
Upload standardized data to HDFS
                |
                v
Run equivalent Hadoop and Spark analytics
```

## 6. Canonical Schema

Every source record will eventually become a record with the same structure:

```json
{
  "record_id": "source-specific-id",
  "source": "consultation",
  "source_split": "train",
  "question": "Normalized question text",
  "answer": "Normalized answer text or URL",
  "answer_type": "text",
  "department": null,
  "related_disease": null,
  "quality_score": null,
  "metadata_origin": "unavailable",
  "question_length": 25,
  "answer_length": 100,
  "question_hash": "sha256-value",
  "duplicate_flag": false
}
```

Observed and inferred metadata must never be mixed silently.

Question text normalization means formatting cleanup only. The project does not
translate, rewrite, medically correct, or change the meaning of questions.

The normalization step:

- Converts missing values to an empty string.
- Joins list-valued questions into one string.
- Converts dictionary-valued questions into JSON text.
- Converts the final value to a string.
- Replaces repeated whitespace with one space.
- Removes leading and trailing spaces.

For duplicate detection, the normalized question is casefolded and hashed with
SHA-256. This means questions that only differ by spacing or capitalization can
be flagged as duplicates, while the original normalized question text remains
available for analysis.

Example:

```text
"  What   causes fever?  "
```

becomes:

```text
What causes fever?
```

## 7. Source Download Strategy

Hugging Face snapshot downloads preserve the original published repository
files:

```text
data/source/consultation/
data/source/encyclopedia/
data/source/knowledge_graph/
data/source/lite/
```

These folders now contain the original published repository files.

The original files are already JSONL, so no Pandas conversion is required.
Pandas, Hadoop, Spark, and normal Python can all read JSONL.

## 8. Storage Size Explanation

The original Huatuo source snapshot is **5.432 GB**, but the processed working
directory becomes much larger during full-data preparation.

This is expected because the raw files only contain the fields published by each
source. The canonical JSONL adds project-specific metadata to every record,
including provenance, quality, length, hash, and duplicate fields:

- `source`
- `source_split`
- `answer_type`
- `metadata_origin`
- `question_length`
- `answer_length`
- `question_hash`
- `duplicate_flag`

JSONL is also plain text, so every field name is repeated on every row. With
more than 34 million records, the repeated keys and added metadata increase the
final canonical file size.

During preprocessing, the project temporarily stores both standardized
per-source intermediate files and the final unified canonical file. Therefore,
the working directory size is not the same as the final dataset size.

```text
Raw source data:             about 5.4 GB
Final canonical data:        20,168,846,076 bytes, about 19 GB
Working directory:           about 41 GB before cleanup
```

After inspection and validation, the intermediate files in
`data/standardized-full/sources/` can be removed to recover disk space. The
important full-data artifact is:

```text
data/standardized-full/huatuo_unified.jsonl
```

Presentation explanation:

> The raw source data is 5.432 GB. The processed canonical dataset is larger
> because every row carries extra provenance, quality, length, hash, and
> duplicate fields. The working folder is larger again because it temporarily
> stores both intermediate standardized files and the final unified output.

## 9. Current Project Structure

```text
config/          Shared rules used by Hadoop and Spark
data/samples/    Tiny example datasets
data/source/     Original downloaded Huatuo repository files
docs/            Local assessment PDFs, ignored by Git
hadoop/          Hadoop Streaming mapper and reducer
preprocessing/   Download, standardize, union, and validate scripts
scripts/         Terminal commands for inspection and execution
spark/           Equivalent PySpark analytics implementation
reports/         Source-integrity and pilot-result evidence
README.md        Short operational guide
journey.md       This project journey
```

## 10. Source Integrity Manifest

Before transformation, every original JSONL file is counted and hashed with
SHA-256:

```bash
bash scripts/create_source_manifest.sh
```

The generated files are:

```text
reports/source_manifest.csv
reports/source_manifest.json
```

The manifest records:

- Original file path
- Byte size
- JSON record count
- SHA-256 checksum

This makes the data pipeline reproducible and provides evidence that the source
files remain unchanged. The ten JSONL source files contain **34,048,913
non-empty JSON records** and **5,431,492,086 bytes**. Repository metadata files
such as README and loader scripts account for the small difference from the
complete snapshot size.

## 11. Pilot Sampling Method

Processing all 34 million records before validating the pipeline would make
development slow and error-prone. A deterministic pilot was therefore created:

```bash
bash scripts/create_pilot.sh
```

The pilot contains exactly 100,000 real records from each source:

| Source          | Validation |      Test |   Train/Full |       Total |
| --------------- | ---------: | --------: | -----------: | ----------: |
| Consultation    |      1,000 |     1,000 | 98,000 train |     100,000 |
| Encyclopedia    |      1,000 |     1,000 | 98,000 train |     100,000 |
| Knowledge Graph |      1,000 |     1,000 | 98,000 train |     100,000 |
| Lite            |        N/A |       N/A | 100,000 full |     100,000 |
| **Combined**    |  **3,000** | **3,000** |  **394,000** | **400,000** |

The pilot uses a deterministic prefix from each source after preserving all
available validation and test records. This makes runs reproducible. It is used
for engineering validation, not for making final population-level conclusions.

Every pilot record receives a `source_split` field so its origin remains
traceable after integration.

## 12. Pilot Preprocessing Results

The pilot was standardized and unioned with:

```bash
bash scripts/prepare_data.sh data/pilot data/processed-pilot
```

Verified results:

| Metric                       |  Result |
| ---------------------------- | ------: |
| Input records                | 400,000 |
| Unified output records       | 400,000 |
| Text answers                 | 300,000 |
| URL answers                  | 100,000 |
| Observed metadata records    | 100,000 |
| Metadata-unavailable records | 300,000 |
| Duplicate questions detected |     709 |
| Duplicate percentage         | 0.1772% |
| Validation status            |   Valid |

The processed pilot occupies approximately 929 MB because the canonical format
adds provenance, derived lengths, hashes, and metadata fields to every record.

## 13. Pilot Analytics Results

All four case studies completed successfully on the 400,000-record pilot.
Hadoop and Spark produced the same output row counts for every case study, which
confirms that the two implementations are analytically equivalent before the
benchmark comparison.

| Case study                  | Output groups |
| --------------------------- | ------------: |
| Department demand           |            16 |
| Disease and symptom trends  |         2,301 |
| QA quality and completeness |             4 |
| Question-type distribution  |             7 |

The Hadoop-versus-Spark timing comparison is reported in Section 15 using
HDFS/YARN benchmark submissions.

### Pilot Analytical Observations

- The 100,000 consultation records contain URL answers, producing a 100% URL
  answer rate for that source.
- The Lite source has an average quality score of **4.12922**, with observed
  scores between 4 and 5.
- Lite questions are the longest on average at **80.15646 characters**.
- Encyclopedia answers are the longest on average at **538.86676 characters**.
- The largest recognized question category is treatment with **68,116**
  questions.
- The second-largest recognized category is diagnosis with **50,621**
  questions.
- The department with the highest observed Lite pilot count is `妇产科`
  with **19,406** records.

Reproducible summary evidence is stored in:

```text
reports/pilot_summary.json
reports/framework_equivalence.json
results/case-benchmark/timings-cluster-20260606-153149.csv
```

## 14. Inspecting the Original Data

Use the inspection script:

```bash
bash scripts/inspect_source_data.sh summary
bash scripts/inspect_source_data.sh samples
```

The summary command displays source sizes and counts all records with a terminal
spinner.

## 15. Inspecting the Full Canonical Data

After the full source files are standardized and unioned, the next step is local
inspection only. Hadoop and Spark should not be submitted until the full
canonical data has been checked.

The inspection command is:

```bash
bash scripts/summarize_full_data.sh
```

It reports local file properties:

```bash
ls -lh data/standardized-full/huatuo_unified.jsonl
du -h data/standardized-full/huatuo_unified.jsonl
wc -l data/standardized-full/huatuo_unified.jsonl
```

It also creates:

```text
reports/full_summary.json
data/samples/full-canonical/
```

These files provide full-data evidence similar to the pilot evidence: total
records, source distribution, answer-type distribution, duplicate percentage,
missing values, length statistics, quality-score statistics, and representative
samples by source.

Full canonical inspection result:

| Metric | Value |
| ------ | ----: |
| Final canonical records | 34,048,898 |
| Final canonical file size | 20,168,846,076 bytes, about 19 GB |
| Invalid JSON lines | 0 |
| Duplicate-flagged records | 10,162,575 |
| Duplicate percentage | 29.847% |
| URL answers | 32,708,326 |
| Text answers | 1,340,572 |
| Missing questions | 0 |
| Missing answers | 0 |

Source distribution:

| Source | Records |
| ------ | ------: |
| Consultation QA | 32,708,331 |
| Encyclopedia QA | 364,420 |
| Knowledge Graph QA | 798,444 |
| Huatuo26M-Lite | 177,703 |

Full-data evidence is stored in:

```text
reports/full_summary.json
data/samples/full-canonical/
```

## 16. Full Preprocessing Runtime

The full-source preprocessing command is:

```bash
bash scripts/prepare_full_data.sh data/source data/standardized-full
```

This command performs:

- Schema normalization for every source split.
- Text normalization for question and answer fields.
- Union into one canonical JSONL file.
- Cross-source duplicate flagging using normalized `question_hash` values.
- Validation of the final canonical file.

Observed execution time:

```text
Full preprocessing runtime: approximately 2 hours 23 minutes
Measured window: 2026-06-06 16:17:30 to about 18:40 +08
Union output write phase: 2 hours 20 minutes 26 seconds
```

The command was started before a timer wrapper was added, so the runtime is
reported from observed output-file timestamps and command completion polling.
Future formal runs should wrap the command with `/usr/bin/time`.

## 17. Current Status

Completed:

- Read and analyzed the assessment requirements.
- Defined four case studies aligned with the available dataset fields.
- Downloaded all four original Huatuo dataset repositories.
- Confirmed the combined dataset exceeds 5 GB.
- Confirmed the combined record count is over 34 million.
- Generated a SHA-256 integrity manifest for every source JSONL file.
- Created a deterministic 400,000-record real-data pilot.
- Implemented the canonical preprocessing pipeline.
- Implemented Hadoop Streaming and PySpark analytics.
- Validated all four case studies against the real-data pilot.
- Confirmed matching Hadoop/Spark pilot aggregate outputs.
- Added simple source-data inspection commands.
- Added a per-case-study benchmark mode for Hadoop and Spark.
- Executed the controlled per-case-study benchmark on HDFS/YARN.
- Completed full-source schema normalization, union, and duplicate flagging.
- Validated the complete canonical dataset.
- Inspected and summarized the complete canonical dataset.
- Added full-canonical-data inspection and sample-generation scripts.

Not yet completed:

- Upload the complete standardized dataset to HDFS.
- Run all four full-dataset Hadoop jobs.
- Run all four full-dataset Spark jobs.
- Produce final result tables, diagrams, and report discussion.

## 18. Benchmark Design

The benchmark measures each analytical question separately. It submits one job
per case study for Hadoop and one job per case study for Spark:

```bash
bash scripts/run_case_benchmark.sh cluster
```

The output CSV has one row per framework per case study:

```text
framework,mode,case_study,elapsed_seconds,output_records,input,output
```

This layout is useful for the presentation because it shows which case study is
more expensive. For example, disease and symptom trend extraction is expected
to be heavier than department demand because it searches more medical terms and
creates more output groups.

The benchmark controls the main comparison points:

- Hadoop and Spark read the same canonical JSONL input.
- Hadoop and Spark execute equivalent analytical logic.
- Each case study is timed separately.
- Each output record count is logged for validation.
- The HDFS/YARN mode is used for the formal cluster comparison.

Formal HDFS/YARN benchmark on the 400,000-record pilot:

| Case study                  | Output groups | Hadoop Streaming on YARN | Spark on YARN |
| --------------------------- | ------------: | -----------------------: | ------------: |
| Department demand           |            16 |                 18.763 s |      29.630 s |
| Disease and symptom trends  |         2,301 |                 18.558 s |      31.256 s |
| QA quality and completeness |             4 |                 19.602 s |      25.309 s |
| Question-type distribution  |             7 |                 18.560 s |      23.310 s |

The timing file is:

```text
results/case-benchmark/timings-cluster-20260606-153149.csv
```

This table is the benchmark used for the Hadoop-versus-Spark comparison. Both
frameworks read the same HDFS input file and write their outputs back to HDFS.
The output-group counts match across frameworks, which confirms that the jobs
produced equivalent aggregate result sizes.

## 19. Next Step

The complete canonical dataset has been created and inspected from all original
source files:

```text
consultation/{train,validation,test}_datasets.jsonl
encyclopedia/{train,validation,test}_datasets.jsonl
knowledge_graph/{train,validation,test}_datasets.jsonl
lite/format_data.jsonl
```

The next implementation step is to upload the complete canonical dataset to HDFS
and then run the formal full-dataset Hadoop and Spark experiments.

The full-source pipeline preserves every source split:

```bash
bash scripts/prepare_full_data.sh data/source data/standardized-full
```

This command produces the complete canonical dataset at:

```text
data/standardized-full/huatuo_unified.jsonl
```

The full canonical file has been inspected with:

```bash
bash scripts/summarize_full_data.sh
```

## 20. Suggested Presentation Storyline

1. Explain the WOC7017 assessment goal and healthcare domain.
2. Introduce the four Huatuo sources and prove the combined 5.432 GB size.
3. Show how heterogeneous schemas create a data-integration challenge.
4. Explain why the records are standardized and unioned.
5. Present the canonical schema and source-integrity manifest.
6. Explain the deterministic 400,000-record pilot methodology.
7. Present the four MapReduce case studies.
8. Show the pilot validation and analytical observations.
9. Present the per-case-study Hadoop-versus-Spark benchmark.
10. Demonstrate the complete HDFS Hadoop-versus-Spark evaluation.
