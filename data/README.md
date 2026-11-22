# Lending Club Data input

The full research uses the project extract called Lending Club Data and the supplied LCDataDictionary.xlsx. The extract contains 2,925,492 unique loan records and 152 columns. Its identity and SHA-256 are recorded in source_identity.json.

Provide the CSV and dictionary through the research runner's --source and --dictionary options. The runner passes those locations to the stage scripts. Every rerun uses the same loan labels, eligibility rules, calendar splits and supplied field definitions. A different extract requires its own data review and study specification.

The source CSV includes all fields listed in research/development_sample_20261108/inputs/application_variable_register.csv. Its issue dates use the source month-year form, and its term values identify 36- or 60-month contracts.

synthetic_applications.csv contains two fabricated records for demonstrating the point calculation. The frozen scorecard and published aggregate evidence can be inspected and used with that example after installing the dependencies.

The full loan extract and generated loan-level tables remain local analysis inputs. The original reference books are cited in the paper and README.
