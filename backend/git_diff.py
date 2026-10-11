import subprocess


def get_commit_diff(commit_id):

    result = subprocess.run(
        [
            "git",
            "show",
            "--format=",
            "--unified=3",
            commit_id
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout

def get_file_diff(commit_id, file_path):
    result = subprocess.run(
        [
            "git",
            "show",
            "--format=",
            "--unified=3",
            commit_id,
            "--",
            file_path
        ],
        capture_output=True,
        text=True,
        check=True
    )

    return result.stdout


def get_all_commit_diffs():

    result = subprocess.run(
        [
            "git",
            "log",
            "--pretty=format:%H"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    commits = result.stdout.splitlines()

    all_diffs = []

    for commit_id in commits:

        diff = get_commit_diff(commit_id)

        all_diffs.append({
            "commit_id": commit_id,
            "diff": diff
        })

    return all_diffs


if __name__ == "__main__":

    all_diffs = get_all_commit_diffs()

    for item in all_diffs:

        print("=" * 60)
        print("COMMIT:", item["commit_id"])
        print("=" * 60)

        print(item["diff"])