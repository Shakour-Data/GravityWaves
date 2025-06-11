// JavaScript for GravityWaves Project Management Gantt Chart and Task Management

document.addEventListener("DOMContentLoaded", function() {
    const tasksTableBody = document.querySelector("#tasks-table tbody");
    const resourcesTableBody = document.querySelector("#resources-table tbody");
    const costSummaryDiv = document.getElementById("cost-summary");
    const ganttDiv = document.getElementById("gantt");

    const taskModal = document.getElementById("task-modal");
    const addTaskBtn = document.getElementById("add-task-btn");
    const closeModalSpan = taskModal.querySelector(".close");
    const taskForm = document.getElementById("task-form");

    let tasks = [];
    let resources = [];

    // Fetch tasks from backend
    function fetchTasks() {
        fetch("/api/tasks")
            .then(response => response.json())
            .then(data => {
                tasks = data;
                renderTasksTable();
                renderGanttChart();
                calculateCost();
            });
    }

    // Fetch resources from backend
    function fetchResources() {
        fetch("/api/resources")
            .then(response => response.json())
            .then(data => {
                resources = data;
                renderResourcesTable();
            });
    }

    // Render tasks table
    function renderTasksTable() {
        tasksTableBody.innerHTML = "";
        tasks.forEach(task => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${task.name}</td>
                <td>${task.duration_days}</td>
                <td>${task.planned_start}</td>
                <td>${task.planned_end}</td>
                <td>${task.actual_start || ""}</td>
                <td>${task.actual_end || ""}</td>
                <td>${task.status}</td>
                <td>${task.assigned_resources.join(", ")}</td>
            `;
            tasksTableBody.appendChild(tr);
        });
    }

    // Render resources table
    function renderResourcesTable() {
        resourcesTableBody.innerHTML = "";
        resources.forEach(res => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${res.name}</td>
                <td>$${res.hourly_rate.toFixed(2)}</td>
            `;
            resourcesTableBody.appendChild(tr);
        });
    }

    // Render Gantt chart using frappe-gantt
    function renderGanttChart() {
        if (!tasks.length) {
            ganttDiv.innerHTML = "<p>No tasks to display.</p>";
            return;
        }
        // Map tasks to frappe-gantt format
        const ganttTasks = tasks.map(task => {
            return {
                id: task.id.toString(),
                name: task.name,
                start: task.planned_start,
                end: task.planned_end,
                progress: task.status === "Done" ? 100 : (task.status === "In Progress" ? 50 : 0),
                dependencies: ""
            };
        });

        // Clear previous gantt if any
        ganttDiv.innerHTML = "";
        const gantt = new Gantt(ganttDiv, ganttTasks, {
            view_mode: 'Day',
            date_format: 'YYYY-MM-DD',
            custom_popup_html: function(task) {
                return `
                    <div class="details-container">
                        <h5>${task.name}</h5>
                        <p>Start: ${task.start}</p>
                        <p>End: ${task.end}</p>
                        <p>Progress: ${task.progress}%</p>
                    </div>
                `;
            }
        });
    }

    // Calculate cost estimation
    function calculateCost() {
        if (!tasks.length || !resources.length) {
            costSummaryDiv.innerHTML = "<p>Insufficient data to calculate cost.</p>";
            return;
        }
        let totalCost = 0;
        tasks.forEach(task => {
            const durationHours = task.duration_days * 8; // Assuming 8 hours per day
            task.assigned_resources.forEach(resName => {
                const res = resources.find(r => r.name === resName.trim());
                if (res) {
                    totalCost += durationHours * res.hourly_rate;
                }
            });
        });
        costSummaryDiv.innerHTML = `<strong>Total Estimated Cost: $${totalCost.toFixed(2)}</strong>`;
    }

    // Show modal
    function showModal() {
        taskModal.style.display = "block";
    }

    // Hide modal
    function hideModal() {
        taskModal.style.display = "none";
        taskForm.reset();
    }

    // Event listeners
    addTaskBtn.addEventListener("click", showModal);
    closeModalSpan.addEventListener("click", hideModal);
    window.addEventListener("click", function(event) {
        if (event.target === taskModal) {
            hideModal();
        }
    });

    // Handle task form submission
    taskForm.addEventListener("submit", function(event) {
        event.preventDefault();
        const formData = new FormData(taskForm);
        const taskData = {
            name: formData.get("name"),
            duration_days: parseInt(formData.get("duration_days")),
            planned_start: formData.get("planned_start"),
            planned_end: formData.get("planned_end"),
            actual_start: formData.get("actual_start") || null,
            actual_end: formData.get("actual_end") || null,
            status: formData.get("status"),
            assigned_resources: formData.get("assigned_resources").split(",").map(s => s.trim()).filter(s => s.length > 0)
        };

        fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                fetchTasks();
                hideModal();
            }
        })
        .catch(err => {
            alert("Error submitting task: " + err);
        });
    });

    // Initial fetch
    fetchResources();
    fetchTasks();
});
