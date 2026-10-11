const API_URL = "http://127.0.0.1:8000";

/* =========================================================
Load Infrastructure Resources
========================================================= */

async function loadResources() {

try {

    const response = await fetch(
        `${API_URL}/infrastructure-resources`
    );

    if (!response.ok) {
        throw new Error(
            `Resource API returned ${response.status}`
        );
    }

    const data = await response.json();

    document.getElementById("resource-count").textContent =
        data.count;


    if (data.resources.length > 0) {

        document.getElementById("provider").textContent =
            data.resources[0].provider;

    } else {

        document.getElementById("provider").textContent =
            "None";
    }


    const resourceList =
        document.getElementById("resource-list");

    resourceList.innerHTML = "";


    data.resources.forEach(resource => {

        const div =
            document.createElement("div");

        div.className = "resource";


        div.innerHTML = `
            <h3>
                ${resource.resource_type}.${resource.resource_name}
            </h3>

            <p>
                <strong>Provider:</strong>
                ${resource.provider}
            </p>

            <p>
                <strong>Terraform File:</strong>
                ${resource.file_path}
            </p>

            <button onclick="toggleHistory(${resource.id})">
                View History
            </button>

            <div
                id="history-${resource.id}"
                class="resource-history"
                style="display: none;"
            ></div>
        `;


        resourceList.appendChild(div);

    });

} catch (error) {

    console.error(
        "Resource API Error:",
        error
    );

    document.getElementById(
        "resource-list"
    ).textContent =
        "Unable to connect to InfraTrace API.";

}


}

/* =========================================================
Resource History
========================================================= */

async function toggleHistory(resourceId) {


const historyDiv =
    document.getElementById(
        `history-${resourceId}`
    );


if (historyDiv.style.display === "block") {

    historyDiv.style.display = "none";

    return;
}


historyDiv.style.display = "block";

historyDiv.textContent =
    "Loading history...";


try {

    const response = await fetch(
        `${API_URL}/infrastructure-resources/${resourceId}/history`
    );


    if (!response.ok) {

        throw new Error(
            `History API returned ${response.status}`
        );

    }


    const data = await response.json();


    if (
        !data.history ||
        data.history.length === 0
    ) {

        historyDiv.textContent =
            "No history found.";

        return;
    }


    historyDiv.innerHTML = "";


    data.history.forEach(change => {

        const item =
            document.createElement("div");

        item.className =
            "history-item";


        item.innerHTML = `
            <p>
                <strong>Change:</strong>
                ${change.change_type || "Unknown"}
            </p>

            <p>
                <strong>Commit:</strong>
                ${change.commit_id}
            </p>

            <p>
                <strong>Author:</strong>
                ${change.author}
            </p>

            <p>
                <strong>Description:</strong>
                ${change.change_description}
            </p>

            <details>

                <summary>
                    Git Diff
                </summary>

                <pre>

${change.diff || "No diff available"} </pre>


            </details>
        `;


        historyDiv.appendChild(item);

    });

} catch (error) {

    console.error(
        "History API Error:",
        error
    );

    historyDiv.textContent =
        "Unable to load history.";

}


}

/* =========================================================
Ask InfraTrace - RAG
========================================================= */

async function askQuestion() {


const question =
    document.getElementById(
        "question"
    ).value.trim();


if (!question) {

    return;
}


const answer =
    document.getElementById(
        "answer"
    );


answer.textContent =
    "Thinking...";


try {

    const response = await fetch(
        `${API_URL}/ask?question=${encodeURIComponent(question)}`
    );


    if (!response.ok) {

        throw new Error(
            `Ask API returned ${response.status}`
        );

    }


    const data =
        await response.json();


    answer.innerHTML = "";


    const answerBox =
        document.createElement("div");

    answerBox.className =
        "ai-answer";


    const title =
        document.createElement("h3");

    title.textContent =
        "AI Answer";


    const answerText =
        document.createElement("p");

    answerText.textContent =
        data.answer;


    answerBox.appendChild(title);

    answerBox.appendChild(answerText);

    answer.appendChild(answerBox);


    if (
        data.sources &&
        data.sources.length > 0
    ) {

        const sourcesBox =
            document.createElement("div");

        sourcesBox.className =
            "sources";


        const sourcesTitle =
            document.createElement("h3");

        sourcesTitle.textContent =
            "Supporting Evidence";


        sourcesBox.appendChild(
            sourcesTitle
        );


        data.sources.forEach(source => {

            const sourceCard =
                document.createElement("div");

            sourceCard.className =
                "source-card";


            sourceCard.innerHTML = `
                <p>
                    <strong>Context ID:</strong>
                    ${source.context_id}
                </p>

                <p>
                    <strong>Resource ID:</strong>
                    ${source.resource_id ?? "N/A"}
                </p>

                <p>
                    <strong>Context Type:</strong>
                    ${source.context_type}
                </p>

                <p>
                    <strong>Similarity Distance:</strong>
                    ${source.distance}
                </p>
            `;


            const details =
                document.createElement(
                    "details"
                );


            const summary =
                document.createElement(
                    "summary"
                );


            summary.textContent =
                "View Evidence";


            const evidence =
                document.createElement(
                    "pre"
                );


            evidence.textContent =
                source.evidence;


            details.appendChild(summary);

            details.appendChild(evidence);

            sourceCard.appendChild(details);

            sourcesBox.appendChild(sourceCard);

        });


        answer.appendChild(sourcesBox);

    }

} catch (error) {

    console.error(
        "InfraTrace API Error:",
        error
    );

    answer.textContent =
        "Unable to connect to InfraTrace API.";

}


}

/* =========================================================
Load Azure Resources
========================================================= */

async function loadAzureResources() {


try {

    const response =
        await fetch(
            `${API_URL}/azure-resources`
        );


    if (!response.ok) {

        throw new Error(
            `Azure API returned ${response.status}`
        );

    }


    const data =
        await response.json();


    document.getElementById(
        "azure-count"
    ).textContent =
        data.count;

} catch (error) {

    console.error(
        "Azure API Error:",
        error
    );

    document.getElementById(
        "azure-count"
    ).textContent =
        "Unavailable";

}


}

/* =========================================================
Terraform ↔ Azure Comparison
========================================================= */

async function loadComparison() {


try {

    const response =
        await fetch(
            `${API_URL}/terraform-azure-comparison`
        );


    if (!response.ok) {

        throw new Error(
            `Comparison API returned ${response.status}`
        );

    }


    const data =
        await response.json();


    /*
     * Comparison Summary
     */

    const summary =
        data.summary;


    document.getElementById(
        "terraform-total"
    ).textContent =
        summary.terraform_resources;


    document.getElementById(
        "azure-total"
    ).textContent =
        summary.azure_resources;


    document.getElementById(
        "matched-total"
    ).textContent =
        summary.matched;


    document.getElementById(
        "missing-total"
    ).textContent =
        summary.missing_in_azure;


    document.getElementById(
        "azure-only-total"
    ).textContent =
        summary.azure_only;


    /*
     * Detailed Comparison
     */

    const comparisonList =
        document.getElementById(
            "comparison-list"
        );


    comparisonList.innerHTML = "";


    if (
        !data.comparison ||
        data.comparison.length === 0
    ) {

        comparisonList.textContent =
            "No comparison data available.";

        return;
    }


    data.comparison.forEach(result => {

        const item =
            document.createElement(
                "div"
            );


        item.className =
            "comparison-item";


        /*
         * Status
         */

        const status =
            document.createElement(
                "h3"
            );


        status.textContent =
            result.status;


        if (
            result.status === "MATCHED"
        ) {

            status.className =
                "status-matched";

        } else if (
            result.status === "NOT_FOUND_IN_AZURE"
        ) {

            status.className =
                "status-missing";

        } else {

            status.className =
                "status-azure-only";
        }


        item.appendChild(status);


        /*
         * Terraform information
         */

        if (result.terraform) {

            const terraform =
                result.terraform;


            const terraformBox =
                document.createElement(
                    "div"
                );


            terraformBox.className =
                "comparison-details";


            terraformBox.innerHTML = `
                <p>
                    <strong>Terraform Resource:</strong>
                    ${terraform.resource_type}.${terraform.resource_name}
                </p>

                <p>
                    <strong>Provider:</strong>
                    ${terraform.provider}
                </p>

                <p>
                    <strong>File:</strong>
                    ${terraform.file_path}
                </p>
            `;


            item.appendChild(
                terraformBox
            );

        }


        /*
         * Azure information
         */

        if (result.azure) {

            const azure =
                result.azure;


            const azureBox =
                document.createElement(
                    "div"
                );


            azureBox.className =
                "comparison-details";


            azureBox.innerHTML = `
                <p>
                    <strong>Azure Resource:</strong>
                    ${azure.name}
                </p>

                <p>
                    <strong>Type:</strong>
                    ${azure.resource_type}
                </p>

                <p>
                    <strong>Resource Group:</strong>
                    ${azure.resource_group}
                </p>

                <p>
                    <strong>Location:</strong>
                    ${azure.location}
                </p>

                <p>
                    <strong>Provisioning State:</strong>
                    ${azure.provisioning_state}
                </p>
            `;


            item.appendChild(
                azureBox
            );

        }


        comparisonList.appendChild(
            item
        );

    });

} catch (error) {

    console.error(
        "Comparison API Error:",
        error
    );

    document.getElementById(
        "comparison-list"
    ).textContent =
        "Unable to load Terraform ↔ Azure comparison.";

}


}

async function toggleAzureResources() {
    const section = document.getElementById(
        "azure-details-section"
    );

    if (section.style.display === "block") {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    const list = document.getElementById(
        "azure-resource-list"
    );

    list.textContent = "Loading Azure resources...";

    try {
        const response = await fetch(
            `${API_URL}/azure-resources/stored`
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        list.innerHTML = "";

        if (data.resources.length === 0) {
            list.textContent = "No Azure resources found.";
            return;
        }

        data.resources.forEach(resource => {
            const card = document.createElement("div");
            card.className = "resource";

            const heading = document.createElement("h3");
            heading.textContent = resource.name;
            card.appendChild(heading);

            const fields = [
                ["Type", resource.resource_type],
                ["Resource Group", resource.resource_group],
                ["Location", resource.location],
                ["Provisioning State", resource.provisioning_state],
                ["Last Synced", resource.last_synced]
            ];

            fields.forEach(([label, value]) => {
                const p = document.createElement("p");
                const strong = document.createElement("strong");

                strong.textContent = `${label}: `;
                p.appendChild(strong);
                p.appendChild(
                    document.createTextNode(value ?? "N/A")
                );

                card.appendChild(p);
            });

            list.appendChild(card);
        });

    } catch (error) {
        console.error("Azure Details Error:", error);
        list.textContent = "Unable to load Azure resources.";
    }
}


/* =========================================================
Start InfraTrace Dashboard
========================================================= */

loadResources();

loadAzureResources();

loadComparison();
