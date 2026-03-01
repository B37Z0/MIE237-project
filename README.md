# MIE237-project
MIE237: Project Assignment (Winter 2026)
Group: Gabriel Faustino, Sunny Wu, Ben Zhou

## Overview

**Task-Switching Experiment** built with Pygame. Participants alternate between two counting tasks under varying complexity and switching intervals, following a 3×3 factorial design.

## Tasks

- **Task 1** — Count total occurences of a specified set of digits in a 10-digit string.
- **Task 2** — Count total occurences of digits **not** in the specified set.

## Experiment Design

| Factor | Levels |
|---|---|
| Complexity (# of target digits) | 1, 2, 3 |
| Switching interval (seconds) | 10, 20, 30 |

- **9 blocks** total (3 complexity levels × 3 intervals), each lasting 2 minutes.
- Complexity order and interval order are randomized.
- 10-second breaks between blocks.

## How to Run

```bash
python MIE237_experiment.py
```

**Requirements:** Python 3, Pygame (`pip install pygame`)

## Data Output

Results are saved to `session_data/` as timestamped CSV files (`results_YYYYMMDD_HHMMSS.csv`). A new file is created only when the experiment is started (not during tutorial).

| Column | Description |
|---|---|
| `trial` | Trial number within that session |
| `complexity` | Number of target digits (1, 2, or 3) |
| `interval` | Switching interval in seconds |
| `task_type` | 1 = count targets, 2 = count non-targets |
| `actual_count` | Correct answer |
| `user_answer` | Participant's response |
| `correct` | 1 if correct, 0 if incorrect |

## Project Structure

```
MIE237-project/
├── MIE237_experiment.py          # Main experiment script
├── session_data/                 # CSV results (auto-created)
├── Project Assignment.pdf        # Assignment specification
├── Project Literature References/  # Reference papers
└── README.md
```
