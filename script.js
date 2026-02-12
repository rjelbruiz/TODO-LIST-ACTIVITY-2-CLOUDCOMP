function createNewTask() {
    const input = document.getElementById('taskInput');
    const taskValue = input.value.trim();

    if (taskValue === "") return;

    const task = document.createElement('div');
    task.className = 'task-card';
    // Adding a random meme prefix
    const vibes = ["✨ ", "🔥 ", "💀 ", "🤡 ", "🤏 "];
    const randomVibe = vibes[Math.floor(Math.random() * vibes.length)];
    
    task.innerText = randomVibe + taskValue;
    
    task.onclick = function() {
        moveTask(this);
    };

    document.getElementById('todo-list').appendChild(task);
    input.value = "";
}

function moveTask(taskElement) {
    const parentId = taskElement.parentElement.id;

    if (parentId === 'todo-list') {
        document.getElementById('progress-list').appendChild(taskElement);
    } else if (parentId === 'progress-list') {
        document.getElementById('done-list').appendChild(taskElement);
        taskElement.innerText += " (W)"; // W for Win
        taskElement.style.background = "#90ee90";
    } else {
        // Instead of just removing, let's alert a classic meme line
        alert("Task Sent to the Shadow Realm.");
        taskElement.remove();
    }
}