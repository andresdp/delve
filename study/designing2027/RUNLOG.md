# Designing 2027 run log

## Setup — 2026-11-08 20:24
- commit: a928214
- codex: codex-cli 0.165.0
- model: gpt-6-luna
- workspaces: ~/Documents/GitHub/ddspace-sandboxes/designing2027/workspaces
- 2026-11-08 20:24 smoke test: fraud-search-M-r1 ok, skills via files
- 2026-11-08 21:02 after smoke: added early_stop/no_explore warnings, prompt asks for default budget; commit 79931d9; pilots next
- 2026-11-08 21:29 pilot 1: E failed (reference not found, stale /4 help), M stopped early; fixes d3210fa + 3d6fdfb (empty HOME per session); rerunning pilots
- 2026-11-08 21:50 pilot 1: E failed (reference not found, stale /4 help), M stopped early; fixes d3210fa + 3d6fdfb (empty HOME per session); rerunning pilots
- 2026-11-08 21:52 pilot 1: E failed (reference not found, stale /4 help), M stopped early; fixes d3210fa + 3d6fdfb (empty HOME per session); rerunning pilots
- 2026-11-08 22:33 pilot 3 (effort high): 4/4 ok, clean checks; skills frozen at 4f9874d
- 2026-11-08 22:34 full run started
- 2026-11-09 11:52 second run (trade-offs, schema 6) at 696139c, into results-v2
- 2026-11-09 second run finished: 36/36 ok, checks clean, describer openai/gpt-5.6-luna, no web/network commands, 4.7 h
- 2026-11-12 the E space names its dimensions as concerns (inputs/dimension_names.yaml), each keeping the model's question as its description; the sessions above ran with the questions as names (same ids)

## Short cases — 2026-11-16 11:56
- branch study/designing2027-short, commit 1cd63d9 (skills as on main 97055cd; newer than the results-v2 run at 696139c, by user decision: no reruns of the old cases)
- codex: codex-cli 0.169.0; model gpt-6-luna, effort high; describer openai/gpt-5.6-luna
- cases: cases-short/ (pumps-search, tickets-explain; 5 requirements each), E,N x 2 reps into results-short/
- E workspace rebuilt with build_workspace.py (dimensions named as concerns) in ~/Documents/GitHub/ddspace-sandboxes/designing2027-short/workspaces
- smoke: pumps-search-N-r1 ok, check ok, skills via files (results-short-smoke/)
- toy: examples/toy-git-hosting/cases-short/ (monorepo-search, monorepo-explain), M,N x 2 reps, each in a fresh folder, with the runner's controls (web search off, same features disabled)
- 2026-11-16 12:48 short run finished: 8/8 ok (results-short/), toy 8/8 ok (examples/toy-git-hosting/runs-short/), checks clean, no web commands
