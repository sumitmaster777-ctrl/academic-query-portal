
const teacherQueries = document.getElementById("teacherQueries");

// Retrieve queries from Flask
async function getSavedQueries() {
    try {
        const response = await fetch("/api/queries");

        if (!response.ok) {
            throw new Error("Unable to retrieve queries");
        }

        return await response.json();

    } catch (error) {
        console.error(error);
        return [];
    }
}

// Update dashboard statistics
function updateStatistics(queries) {
    document.getElementById("totalQueries").textContent =
        queries.length;

    document.getElementById("pendingQueries").textContent =
        queries.filter(q => q.status === "Pending").length;

    document.getElementById("progressQueries").textContent =
        queries.filter(q => q.status === "In Progress").length;

    document.getElementById("resolvedQueries").textContent =
        queries.filter(q => q.status === "Resolved").length;
}

// Display all student queries
async function displayTeacherQueries() {
    const queries = await getSavedQueries();

    teacherQueries.innerHTML = "";
    updateStatistics(queries);

    if (queries.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 6;
        cell.textContent = "No student queries available.";

        row.appendChild(cell);
        teacherQueries.appendChild(row);
        return;
    }

    queries.forEach(function(query) {
        const row = document.createElement("tr");

        const details = [
            query.id,
            query.studentName,
            query.course,
            query.category,
            query.description
        ];

        details.forEach(function(value) {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
        });

        // Create status dropdown
        const statusCell = document.createElement("td");
        const statusSelect = document.createElement("select");

        ["Pending", "In Progress", "Resolved"].forEach(function(status) {
            const option = document.createElement("option");

            option.value = status;
            option.textContent = status;

            if (query.status === status) {
                option.selected = true;
            }

            statusSelect.appendChild(option);
        });

        // Update status through Flask
        statusSelect.addEventListener("change", async function() {
            statusSelect.disabled = true;

            try {
                const csrfToken = document.querySelector(
                    'meta[name="csrf-token"]'
                ).getAttribute("content");

                const response = await fetch(
                    "/api/queries/" + encodeURIComponent(query.id),
                    {
                        method: "PUT",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": csrfToken
                        },
                        body: JSON.stringify({
                            status: statusSelect.value
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error("Status update failed");
                }

                await displayTeacherQueries();

            } catch (error) {
                alert("Unable to update query status.");
                console.error(error);
                await displayTeacherQueries();
            }
        });

        statusCell.appendChild(statusSelect);
        row.appendChild(statusCell);

        teacherQueries.appendChild(row);
    });
}

// Load queries when dashboard opens
displayTeacherQueries();
