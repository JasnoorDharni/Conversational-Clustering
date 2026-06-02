# Oracle Evaluation Prompt - H3 Proxy Validity
**Version:** v2.0  
**Status:** Locked before refreshed oracle ratings are collected.  
**Used in:** H3 qualitative forced-choice proxy evaluation

---

You are evaluating two anonymized alternative clusterings of the same conflict-event data from the Russia-Ukraine war (2022-2024).

Your task is to choose which clustering is more meaningful for conflict-event analysis.

Judge only the clustering quality shown in the descriptions below. Ignore option position. Do not prefer:
- the first option
- the second option
- the longer option
- the shorter option
- the more detailed option
- the newer-looking option

The options are anonymized. You do not know which experimental condition produced them, and you must not infer quality from metadata or presentation order.

Use these criteria only:
- internal coherence within clusters
- interpretability of clusters as meaningful categories
- separation between clusters
- usefulness for understanding conflict-event patterns

Do not use:
- label position
- verbosity
- formatting differences
- assumptions about which method "should" be better

---

## Option A

{option_a}

---

## Option B

{option_b}

---

## Output format

Return strict JSON with this schema:

```json
{{"choice":"A","confidence":0.73,"reason":"brief explanation"}}
```

Rules:
- `choice` must be exactly `"A"` or `"B"`
- `confidence` must be a number between `0.0` and `1.0`
- `reason` must be brief and based only on clustering quality
- return JSON only, with no markdown and no extra text
