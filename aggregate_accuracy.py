import argparse
import csv
from collections import defaultdict
from pathlib import Path


REQUIRED_COLUMNS = {
    "trial",
    "complexity",
    "interval_length",
    "task_type",
    "actual_count",
    "user_answer",
    "correct",
}

COMPLEXITY_LABELS = {
    "1": "Easy",
    "2": "Medium",
    "3": "Hard",
}

COMPLEXITY_ORDER = {
    "Easy": 1,
    "Medium": 2,
    "Hard": 3,
}


def aggregate_accuracy(input_folder: Path, output_file: Path) -> None:
    grouped_results = defaultdict(lambda: {"correct": 0, "attempts": 0})
    csv_files = sorted(input_folder.glob("*.csv"))
    participant_ids = {
        csv_path: index
        for index, csv_path in enumerate(csv_files, start=1)
    }

    for csv_path in csv_files:
        with csv_path.open("r", newline="") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                continue

            missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing_columns:
                raise ValueError(
                    f"{csv_path.name} is missing required columns: "
                    f"{', '.join(sorted(missing_columns))}"
                )

            participant = participant_ids[csv_path]

            for row in reader:
                complexity = (row.get("complexity") or "").strip()
                interval_length = (row.get("interval_length") or "").strip()
                correct = (row.get("correct") or "").strip()

                # Ignore blank rows or summary rows appended beside the trial data.
                if not complexity or not interval_length or correct not in {"0", "1"}:
                    continue

                complexity_label = COMPLEXITY_LABELS.get(complexity, complexity)
                key = (participant, complexity_label, interval_length)
                grouped_results[key]["attempts"] += 1
                grouped_results[key]["correct"] += int(correct)

    with output_file.open("w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "participant",
            "complexity",
            "interval_length",
            "tasks_completed",
            "accuracy",
        ])

        sorted_rows = sorted(
            grouped_results.items(),
            key=lambda item: (
                item[0][0],
                COMPLEXITY_ORDER.get(item[0][1], 999),
                item[0][2],
            ),
        )

        for (participant, complexity, interval_length), counts in sorted_rows:
            accuracy = counts["correct"] / counts["attempts"]
            writer.writerow([
                participant,
                complexity,
                interval_length,
                counts["attempts"],
                accuracy,
            ])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine participant CSV files into one accuracy summary CSV."
    )
    parser.add_argument(
        "input_folder",
        nargs="?",
        default="session_data",
        help="Folder containing participant CSV files. Default: session_data",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="participant_accuracy.csv",
        help="Output CSV file path. Default: participant_accuracy.csv",
    )
    args = parser.parse_args()

    input_folder = Path(args.input_folder)
    output_file = Path(args.output_file)

    if not input_folder.exists() or not input_folder.is_dir():
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    aggregate_accuracy(input_folder, output_file)


if __name__ == "__main__":
    main()
