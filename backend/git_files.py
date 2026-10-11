import subprocess


def get_changed_files(commit_id):

    result = subprocess.run(
        [
            "git",
            "show",
            "--pretty=",
            "--name-only",
            commit_id
        ],
        capture_output=True,
        text=True,
        check=True
    )

    files = []

    for line in result.stdout.splitlines():
        line = line.strip()

        if line:
            files.append(line)

    return files


if __name__ == "__main__":

    commit_id = "cf48138c081636dfc9741f831f3e51c1519afe84"

    files = get_changed_files(commit_id)

    print("Files changed in commit:")

    for file in files:
        print(file)