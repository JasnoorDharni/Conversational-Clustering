# Interpreter Prompt — v0 PLACEHOLDER
# Status: NOT READY. Person 1 must write and commit the real prompt here
#         before any Condition B or C run is executed.
#
# Variables injected at runtime (use {variable_name} syntax):
#   {cluster_summary}   — a text description of current clusters
#                         (top 3 events per cluster, silhouette score)
#   {user_instruction}  — the natural-language refinement instruction from the user
#
# The model must respond with a JSON object (and nothing else) of the form:
# {
#   "feature_weights": {"latitude": 1.0, "longitude": 1.0, "adm1": 1.0,
#                       "event_type": 1.0, "actor": 1.0, "fatalities": 1.0},
#   "rationale": "one sentence explaining the parameter change"
# }
# All weights default to 1.0. Increase to emphasise, decrease to de-emphasise.
# Weights must be non-negative floats.

YOU ARE A PLACEHOLDER. REPLACE THIS ENTIRE FILE BEFORE RUNNING ANY EXPERIMENT.
