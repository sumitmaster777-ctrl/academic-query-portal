
const teacherQueries = document.getElementById("teacherQueries");

function getSavedQueries() {
    return JSON.parse(localStorage.getItem("academicQueries")) || [];
}

// Update dashboard statistics
function updateStatistics(queries) {
    document.getElementById("totalQueries").textContent = queries.length;

    document.getElementById("pendingQueries").textContent =
        queries.filter(q => q.status === "Pending").length;

    document.getElementById("progressQueries").textContent =
        queries.filter(q => q.status === "In Progress").length;

    document.getElementById("resolvedQueries").textContent =
        queries.filter(q => q.status === "Resolved").length;
}

// Display all student queries
function displayTeacherQueries() {
    const queries = getSavedQueries();

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

        // Save status when teacher changes it
        statusSelect.addEventListener("change", function() {
            const savedQueries = getSavedQueries();

            const selectedQuery = savedQueries.find(
                q => q.id === query.id
            );

            if (selectedQuery) {
                selectedQuery.status = statusSelect.value;

                localStorage.setItem(
                    "academicQueries",
                    JSON.stringify(savedQueries)
                );

                displayTeacherQueries();
            }
        });

        statusCell.appendChild(statusSelect);
        row.appendChild(statusCell);

        teacherQueries.appendChild(row);
    });
}

displayTeacherQueries();
