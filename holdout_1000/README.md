# V8 synthetic holdout

The 1,000 bilingual notices use 38 newly written scenario families and six document layouts. Each family has clean and incorrect instances. An incorrect instance changes one annotated fact in the target language. The direction column identifies the reference language. Context headings and signoffs vary within each domain, and numeric slots vary where the scenario supports them.

The generator doubles every joint stratum of the prior 500-case benchmark across domain, difficulty, direction, and expected status. Totals are 600 routine, 300 difficult, and 100 edge. There are 700 clean and 300 incorrect cases, with 600 English-source and 400 Chinese-source cases. Domain counts are 300 school, 300 government, 200 public email, and 200 instructions.

Every notice is unique within its language, and no normalized full notice exactly matches the 500-case benchmark. The dataset is synthetic and generated from shared scenario families, so the 1,000 scores are correlated within families. The reference labels come from bilingual scenario construction and controlled mutations, with no independent human adjudication. Document framing is intentionally common across the benchmark and can itself contribute to alignment failures. A diagnostic check also stripped the framing from one clean instance of each scenario family. None of the 38 bare scenario bodies matched V8’s structured parser.

The Colab runner checks the dataset hash and uses the original V7 and V8 source bundles. Its scoring counts a notice as flagged if any output row has a warning. Explanation correctness requires a separate review of the flagged fact against the annotation. The scored CSV includes all warning text and each reference difference for that purpose.

- `v8_holdout_1000.csv` contains the test inputs and reference labels.
- `V8_holdout_1000.ipynb` runs both checkers on the full dataset.
- `scenarios.txt` and `build.py` reproduce the dataset and notebook.
- `score.py` checks exported predictions and produces the row-by-row CSV and aggregate metrics.
