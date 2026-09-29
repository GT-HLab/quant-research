# quant-research

# quant-research

Independent research on factor investing across developed markets, with a focus on **The Japan Factor Puzzle**: why Japanese equities break the most robust anomaly in asset pricing, and what that says about how factor premia work.

All analysis uses the Kenneth French developed-markets data library (North America, Europe, Japan, Asia Pacific ex Japan; monthly returns, November 1990 – mid-2026). Code, notebooks and articles are fully reproducible from public data.

---

## The Japan Factor Puzzle

| Part | Title | Article | Notebook | Status |
|---|---|---|---|---|
| 1 | All of the Crash Risk, None of the Premium | [PDF](articles/Momentum's%20Regional%20Problem.pdf) | [`momentum_regional_analysis.ipynb`](notebooks/momentum_regional_analysis.ipynb) | Published |
| 2 | The Rescue That Wasn't Quite | [PDF](articles/The%20Japan%20Factor%20Puzzle,%20Part%202-%20The%20Rescue%20That%20Wasn't%20Quite.pdf) | [`value_momentum_combination.ipynb`](notebooks/value_momentum_combination.ipynb) | Published |
| 3 | Factor timing and exposure | — | — | In progress |
| 4 | Pure-factor decomposition: real anomaly or construction artifact? | — | — | Planned |

### Part 1 — Momentum: all of the crash risk, none of the premium

- **The dispersion:** $1 in European or Asia ex Japan momentum grew to ~$28 over 35 years; North America ~$6; **Japan $1.10**.
- **Significance:** momentum t-statistics range from 4.80 (Europe) to **0.59 (Japan)**. Japan is insignificant in every sub-period (1990–99, 2000–12, 2013–26): not a decaying premium, not one bad decade.
- **Three regimes elsewhere:** North America decayed, Asia ex Japan strengthened, Europe persisted. Japan fits none of them.
- **Crash without repair:** Japanese momentum's drawdown (−42%) is as deep as other regions', but it has never recovered its prior peak since its February 2012 trough.
- **The puzzle:** Japanese momentum is correlated with the global factor (0.47 to North America, 0.42 to Europe, rising over time). It carries the global factor's risk while paying no measurable premium.

### Part 2 — Value: the rescue that wasn't quite

- **Value works in Japan:** 4.9% annualized, Sharpe 0.45, t = 2.68. But it is ordinary, not exceptional: Asia ex Japan (7.2%, t = 4.12) and Europe (4.3%, t = 2.81) are comparable or stronger.
- **Weakest offset where it matters most:** value–momentum correlation is negative everywhere (−0.32 Europe to **−0.21 Japan**). Japan, the region that most needs the offset, has the weakest one.
- **Japan is the only region where a 50/50 combination lowers risk-adjusted return:** combo Sharpe 0.39 vs. value alone 0.45. Elsewhere the combo adds 0.07–0.45 of Sharpe.
- **A risk story, not a return story:** the combo cuts Japan's worst drawdown from −46% (value) to −35%, the smallest improvement of the four regions (Europe: −31 points).
- **Reform coda:** Japanese value earned 11.4% (t = 3.87) in 2000–2012, then faded to 3.5% (t = 1.10) through the 2013+ governance-reform era, recovering only after the 2023 Tokyo Stock Exchange price-to-book push.

---

## Repository structure

```
articles/    # Published write-ups (PDF)
notebooks/   # Analysis notebooks, one per article
src/         # Reusable modules (Ken French data download and parsing)
scripts/     # One-off scripts and backtests
tests/       # Unit tests
data/        # Raw and processed data (gitignored, downloaded on first run)
```

## Reproduce

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

Data is downloaded directly from the Ken French Data Library by `src/ken_french.py`; no credentials required.

## Methodology and limitations

- Academic long-short decile-sort factors (value = HML, momentum = WML 12-1); raw self-financing returns, no risk-free adjustment.
- No transaction costs, shorting costs or implementation constraints. Decile sorts are not investable portfolios.
- Sample begins November 1990, which excludes the strong early decades of US momentum.
- Japan's momentum result is a **failure to reject zero, not a demonstration of zero**.
- A Barra-style, exposure-neutralized construction would decompose the same phenomenon differently. That is the subject of Part 4.

---

*Personal research; views are my own.*
