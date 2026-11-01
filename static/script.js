
const queryForm = document.getElementById("queryForm");
const successMessage = document.getElementById("successMessage");
const emailInput = document.getElementById("student-email");
const queriesContainer = document.getElementById("queriesContainer");

emailInput.addEventListener("input", function () {
    emailInput.setCustomValidity("");
});

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
        queriesContainer.textContent = "Unable to load queries.";
        return [];
    }
}

// Display submitted queries
async function displayQueries() {
    const queries = await getSavedQueries();

    queriesContainer.innerHTML = "";

    if (queries.length === 0) {
        queriesContainer.textContent =
            "You haven't submitted any queries yet.";
        return;
    }

    queries.forEach(function (query) {
        const card = document.createElement("div");
        card.className = "query-card";

        const heading = document.createElement("h3");
        heading.textContent = "Query ID: " + query.id;

        const category = document.createElement("p");
        category.textContent = "Category: " + query.category;

        const description = document.createElement("p");
        description.textContent =
            "Description: " + query.description;

        const date = document.createElement("p");
        date.textContent = "Submitted: " + query.submittedAt;

        const status = document.createElement("span");
        status.className = "query-status";
        status.textContent = query.status;

        card.append(heading, category, description, date, status);
        queriesContainer.appendChild(card);
    });
}

// Handle form submission
queryForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!queryForm.checkValidity()) {
        queryForm.reportValidity();
        return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(emailInput.value.trim())) {
        emailInput.setCustomValidity(
            "Please enter a valid email address."
        );
        emailInput.reportValidity();
        return;
    }

    const query = {
        studentName: document.getElementById("student-name").value.trim(),
        email: emailInput.value.trim(),
        course: document.getElementById("student-course").value.trim(),
        category: document.getElementById("query-category").value,
        description: document.getElementById("query-description").value.trim()
    };

    try {
        const response = await fetch("/api/queries", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(query)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Query submission failed");
        }

        successMessage.textContent =
            "Thank you, " + query.studentName +
            "! Your query has been saved. Query ID: " +
            result.query_id;

        queryForm.reset();

        await displayQueries();

    } catch (error) {
        successMessage.textContent =
            "Unable to submit your query. Please try again.";

        console.error(error);
    }
});

// Load queries when page opens
displayQueries();
setInterval(displayQueries, 5000);