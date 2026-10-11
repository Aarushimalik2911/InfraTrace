import subprocess


def get_git_history():
    result = subprocess.run(
        [
            "git",
            "log",
            "--pretty=format:%H|%an|%ad|%s",
            "--date=iso"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    commits = []

    for line in result.stdout.splitlines():
        parts = line.split("|", 3)

        if len(parts) == 4:
            commits.append({
                "commit_id": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3]
            })

    return commits


if __name__ == "__main__":
    history = get_git_history()

    for commit in history:
        print(commit)