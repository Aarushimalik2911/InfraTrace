
import re


def parse_tags(configuration):

    tags = {}

    inside_tags = False

    for line in configuration.splitlines():

        line = line.strip()

        if line.startswith("tags") and "=" in line:
            inside_tags = True
            continue

        if inside_tags:

            if line == "}":
                inside_tags = False
                continue

            match = re.match(r'(\w+)\s*=\s*"([^"]*)"', line)

            if match:
                key = match.group(1)
                value = match.group(2)

                tags[key] = value

    return tags


def parse_terraform_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    resources = []

    resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'

    matches = list(re.finditer(resource_pattern, content))

    for match in matches:

        resource_type = match.group(1)
        resource_name = match.group(2)

        start = match.start()

        # Find the closing brace of this Terraform resource
        brace_count = 0
        end = None

        for position in range(match.end() - 1, len(content)):

            if content[position] == "{":
                brace_count += 1

            elif content[position] == "}":
                brace_count -= 1

                if brace_count == 0:
                    end = position + 1
                    break

        if end is None:
            end = len(content)

        configuration = content[start:end]

        # Extract simple attributes
        attributes = {}

        for line in configuration.splitlines():

            line = line.strip()

            attribute_match = re.match(
                r'(\w+)\s*=\s*"([^"]*)"',
                line
            )

            if attribute_match:

                key = attribute_match.group(1)
                value = attribute_match.group(2)

                attributes[key] = value

        # Extract tags
        tags = parse_tags(configuration)

        resources.append({
            "resource_type": resource_type,
            "resource_name": resource_name,
            "attributes": attributes,
            "tags": tags,
            "configuration": configuration
        })

    return resources


if __name__ == "__main__":

    file_path = "infrastructure/terraform/main.tf"

    resources = parse_terraform_file(file_path)

    for resource in resources:

        print("=" * 60)

        print("Resource Type:", resource["resource_type"])
        print("Resource Name:", resource["resource_name"])

        print("\nAttributes:")

        for key, value in resource["attributes"].items():
            print(f"{key}: {value}")

        print("\nTags:")

        for key, value in resource["tags"].items():
            print(f"{key}: {value}")

        print("\nFull Configuration:")
        print(resource["configuration"])
