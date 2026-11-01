
const queryForm = document.getElementById("queryForm");
const successMessage = document.getElementById("successMessage");
const emailInput = document.getElementById("student-email");
const queriesContainer = document.getElementById("queriesContainer");

emailInput.addEventListener("input", function() {
    emailInput.setCustomValidity("");
});

// Retrieve saved queries
function getSavedQueries() {
    return JSON.parse(localStorage.getItem("academicQueries")) || [];
}

// Display saved queries
function displayQueries() {
    const queries = getSavedQueries();

    queriesContainer.innerHTML = "";

    if (queries.length === 0) {
        queriesContainer.textContent = "You haven't submitted any queries yet.";
        return;
    }

    queries.forEach(function(query) {
        const card = document.createElement("div");
        card.className = "query-card";

        const heading = document.createElement("h3");
        heading.textContent = "Query ID: " + query.id;

        const category = document.createElement("p");
        category.textContent = "Category: " + query.category;

        const description = document.createElement("p");
        description.textContent = "Description: " + query.description;

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
queryForm.addEventListener("submit", function(event) {
    event.preventDefault();

    if (!queryForm.checkValidity()) {
        queryForm.reportValidity();
        return;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(emailInput.value.trim())) {
        emailInput.setCustomValidity("Please enter a valid email address.");
        emailInput.reportValidity();
        return;
    }

    const query = {
        id: "Q" + Date.now(),
        studentName: document.getElementById("student-name").value.trim(),
        email: emailInput.value.trim(),
        course: document.getElementById("student-course").value.trim(),
        category: document.getElementById("query-category").value,
        description: document.getElementById("query-description").value.trim(),
        status: "Pending",
        submittedAt: new Date().toLocaleString()
    };

    const queries = getSavedQueries();
    queries.push(query);

    localStorage.setItem("academicQueries", JSON.stringify(queries));

    successMessage.textContent =
        "Thank you, " + query.studentName +
        "! Your query has been saved. Query ID: " + query.id;

    queryForm.reset();

    displayQueries();
});

// Display existing queries when page opens
displayQueries();


// Automatically refresh queries when another tab changes their status
window.addEventListener("storage", function(event) {
    if (event.key === "academicQueries") {
        displayQueries();
    }
});
