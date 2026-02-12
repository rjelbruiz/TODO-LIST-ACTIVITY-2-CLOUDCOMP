const API_URL = 'http://127.0.0.1:5000/tasks';



// 1. Load tasks from the Database when the page opens
document.addEventListener('DOMContentLoaded', async () => {
    const response = await fetch(API_URL);
    const tasks = await response.json();
    tasks.forEach(task => renderTask(task));
});

// 2. Add a new task to the Database
async function createNewTask() {
    const input = document.getElementById('taskInput');
    const taskValue = input.value.trim();
    if (taskValue === "") return;

    // Your classic meme prefix logic
    const vibes = ["✨ ", "🔥 ", "💀 ", "🤡 ", "🚀 "];
    const randomVibe = vibes[Math.floor(Math.random() * vibes.length)];
    const fullText = randomVibe + taskValue;

    // POST to Python
    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: fullText })
    });

    const newTask = await response.json();
    renderTask(newTask);
    input.value = "";
}

// 3. Helper to display the task on the UI
function renderTask(task) {
    const taskCard = document.createElement('div');
    taskCard.className = 'task-card';
    taskCard.innerText = task.text;
    taskCard.id = `task-${task.id}`; // Unique ID for finding it later
    
    // Apply "Completed" styles if saved in DB as 'done'
    if (task.status === 'done') {
        taskCard.style.background = "#90ee90";
    }

    taskCard.onclick = () => moveTask(taskCard, task.id);

    // Append to the correct column based on DB status
    const columnId = task.status === 'todo' ? 'todo-list' : 
                     task.status === 'progress' ? 'progress-list' : 'done-list';
    document.getElementById(columnId).appendChild(taskCard);
}

// 4. Update or Delete from Database
async function moveTask(taskElement, id) {
    const parentId = taskElement.parentElement.id;
    let newStatus = "";

    if (parentId === 'todo-list') {
        newStatus = 'progress';
        document.getElementById('progress-list').appendChild(taskElement);
    } else if (parentId === 'progress-list') {
        newStatus = 'done';
        document.getElementById('done-list').appendChild(taskElement);
        // UI logic (The backend will also handle the (W) in the DB)
        if (!taskElement.innerText.includes("(W)")) {
            taskElement.innerText += " (W)";
        }
        taskElement.style.background = "#90ee90";
    } else {
        // DELETE from DB (Shadow Realm)
        await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        alert("Task Sent to the Shadow Realm.");
        taskElement.remove();
        return;
    }

    // PUT request to update status in SQLite
    await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
}