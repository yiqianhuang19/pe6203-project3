# PE6203 Project 3 — Harness Hyperparameter Optimization

This package documents and reproduces the completed Project 3 experiment. It evaluates a fixed **PI Agent** harness on selected **SkillsBench v1.1** tasks, tunes exposed harness configuration only, and compares four search methods.

## Experiment at a glance

- **Harness:** PI Agent `0.73.1`, run inside Docker containers through WSL2.
- **Model provider:** OpenRouter.
- **Model:** `openai/gpt-4o-mini`.
- **Benchmark:** SkillsBench `v1.1`.
- **Formal validation tasks:** `paper-anonymizer`, `edit-pdf`.
- **Held-out test tasks:** `offer-letter-generator`, `court-form-filling`.
- **Pilot only:** `dialogue-parser` was used for early calibration and is excluded from the formal validation score.

The search space and test split were frozen before held-out testing; see `configs/search_space.json` and `results/summaries/hpo_protocol_frozen.json`.

## Methods compared

1. Default configuration.
2. Random search (fixed seed `6203`).
3. Bayesian optimization via categorical Thompson sampling with Beta–Bernoulli success posteriors.
4. A custom cost-aware, two-stage screening-and-promotion method.

The configuration-selection rule was fixed before testing: maximize validation pass@1, then minimize mean immediate cost estimate, then minimize mean elapsed time.

## Main outcome

`final_c0_off_default` was frozen as the final configuration:

```text
thinking=off, tool profile=default, prompt style=default
```

It passed both untouched held-out tasks: **held-out pass@1 = 2/2 = 1.0**.

This is a small benchmark experiment. The result should not be presented as evidence of broad generalization.

## Repository layout

```text
configs/                 Frozen search space and protocol information
notebooks/               Executed experiment notebook (interactive key entry; no key saved)
results/summaries/       Method-level JSON summaries and frozen-selection record
results/final_runs/      Final held-out task summary JSON files
results/analysis_artifacts/
                          CSV tables, analysis notes, and the generated figure
scripts/rebuild_analysis.py
                          Recreates comparison CSV files and figure from packaged JSON
scripts/verify_results.py
                          Checks that packaged summaries are internally consistent
requirements.txt         Python packages required for notebook analysis
```

## Reproduce the analysis without API calls

The packaged result files can be checked and plotted without OpenRouter, Docker, WSL, or an API key.

```powershell
cd project3_reproducible
python -m pip install -r requirements.txt
python scripts/verify_results.py
python scripts/rebuild_analysis.py
```

The regenerated files are written to `results/rebuilt_analysis/`.

## Re-run the full harness experiment (uses API credits)

Full re-execution requires the following external prerequisites:

1. Windows WSL2 distribution named `Project3-Ubuntu`.
2. Docker Desktop running with WSL integration.
3. PI Agent `0.73.1` installed in the WSL environment.
4. SkillsBench v1.1 source available locally. Update the notebook path cell if it is stored elsewhere.
5. A funded OpenRouter API key, entered only at the notebook prompt or supplied through the environment variable `OPENROUTER_API_KEY`.

Open `notebooks/project3_pi_hpo_experiment.ipynb` in JupyterLab and run setup cells in order. Do **not** use “Run All”: the search and test cells incur API charges. Keep the validation/test split unchanged and do not tune after observing held-out test results.

## Cost reporting note

OpenRouter per-request usage can settle after a request finishes. Therefore, the method-level `cumulative_cost_usd_observed` fields in `results/summaries/` are the primary cost metric. Individual `cost_usd` values are retained as immediate estimates only. The default-method observed cost includes the early dialogue-parser pilot and should not be directly compared with the other methods' formal-validation budgets.

## Security

Never commit an OpenRouter API key, `.env` file, browser credential, Docker credential, or WSL configuration containing a key. This repository contains no secret key.
