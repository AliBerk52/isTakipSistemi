// --- BİLDİRİM SİSTEMİ ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : '⚠️'}</span> <div>${message}</div>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('fadeOut');
        toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
}

// --- VERİTABANI SİMÜLASYONU ---
let users = ['Admin', 'Ahmet Yılmaz', 'Ali Berk', 'Ayşe Kaya'];
let projects = [{
    id: 1,
    name: 'Yazılım Altyapısı Yenileme',
    admin: 'Ahmet Yılmaz',
    team: ['Ali Berk'],
    tasks: [{ id: 101, title: 'Veritabanı Optimizasyonu', assignee: 'Ali Berk', status: 'todo' }],
    logs: []
}];

let activeUser = 'Ahmet Yılmaz'; 
let currentStatusTaskId = null; 
let currentStatusProjectId = null;

// --- SAYFA VE YETKİ YÖNETİMİ ---
function switchUser() {
    activeUser = document.getElementById('userSimulator').value;
    document.querySelectorAll('.menu-item').forEach(i => i.style.display = 'none');
    
    if(activeUser === 'Admin') {
        document.getElementById('menu-manager-projects').style.display = 'flex';
        navTo('page-manager', document.getElementById('menu-manager-projects'));
        renderManagerPage();
    } else {
        let managedProjects = projects.filter(p => p.admin === activeUser);
        if(managedProjects.length > 0) {
            document.getElementById('menu-admin-board').style.display = 'flex';
            document.getElementById('menu-admin-inbox').style.display = 'flex';
            navTo('page-admin-board', document.getElementById('menu-admin-board'));
            renderAdminBoard(managedProjects[0]); 
            renderAdminInbox(managedProjects[0]);
        } else {
            document.getElementById('menu-employee-tasks').style.display = 'flex';
            navTo('page-employee-tasks', document.getElementById('menu-employee-tasks'));
            renderEmployeeTasks();
        }
        if(managedProjects.length > 0) document.getElementById('menu-employee-tasks').style.display = 'flex';
        else renderEmployeeTasks();
    }
    showToast(`${activeUser} olarak giriş yapıldı.`, 'success');
}

function navTo(pageId, menuItem) {
    document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
    menuItem.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
}

// --- MODAL KONTROLLERİ ---
function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

// --- YÖNETİCİ: PROJE VE LİDER OLUŞTURMA ---
function renderManagerPage() {
    let container = document.getElementById('managerProjectsList');
    container.innerHTML = '';
    projects.forEach(p => {
        container.innerHTML += `<div class="card"><h3>${p.name}</h3><div style="color: #94a3b8; font-weight: 600;">👑 Admin: <span style="color:#1e293b;">${p.admin}</span></div></div>`;
    });
    let select = document.getElementById('newProjAdmin');
    select.innerHTML = '';
    users.filter(u => u !== 'Admin').forEach(u => select.innerHTML += `<option value="${u}">${u}</option>`);
}

function createProject() {
    let name = document.getElementById('newProjName').value;
    let admin = document.getElementById('newProjAdmin').value;
    if(!name) return showToast('Proje adı boş olamaz!', 'error');
    projects.push({ id: Date.now(), name: name, admin: admin, team: [], tasks: [], logs: [] });
    closeModal('newProjectModal');
    document.getElementById('newProjName').value = '';
    renderManagerPage();
    showToast('Proje başarıyla oluşturuldu.');
}

// --- PROJE ADMİNİ: TAKIM VE PANO YÖNETİMİ ---
function getInitials(name) { return name.split(' ').map(n => n[0]).join('').substring(0,2); }

function renderAdminBoard(project) {
    if(!project) return;
    document.getElementById('adminProjectTitle').innerText = project.name;
    document.getElementById('adminProjectTeamText').innerText = "Proje Takımı: " + (project.team.length > 0 ? project.team.join(", ") : "Henüz kimse yok");

    ['todo', 'progress', 'blocked', 'done'].forEach(s => {
        document.getElementById(`list-${s}`).innerHTML = '';
        document.getElementById(`count-${s}`).innerText = '0';
    });

    project.tasks.forEach(task => {
        let color = task.status === 'done' ? '#94a3b8' : (task.status === 'blocked' ? '#ef4444' : (task.status === 'progress' ? '#10b981' : '#3b82f6'));
        let taskHtml = `
        <div class="task" draggable="true" data-id="${task.id}" style="border-left-color: ${color}; ${task.status === 'done' ? 'opacity:0.6;' : ''}">
            <div class="task-title">${task.title}</div>
            <div style="display: flex; align-items: center; font-size: 0.85rem; color: #94a3b8; font-weight:600;">
                <span class="user-avatar" style="display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:50%; background:#3b82f6; color:white; font-size:0.75rem; margin-right:8px;">${getInitials(task.assignee)}</span> ${task.assignee}
            </div>
        </div>`;
        document.getElementById(`list-${task.status}`).innerHTML += taskHtml;
        let countEl = document.getElementById(`count-${task.status}`);
        countEl.innerText = parseInt(countEl.innerText) + 1;
    });

    setupDragAndDrop(project);

    let teamSelect = document.getElementById('newTeamMember');
    teamSelect.innerHTML = '';
    users.filter(u => u !== 'Admin' && u !== activeUser && !project.team.includes(u)).forEach(u => teamSelect.innerHTML += `<option value="${u}">${u}</option>`);

    let taskSelect = document.getElementById('taskAssignee');
    taskSelect.innerHTML = '';
    project.team.forEach(u => taskSelect.innerHTML += `<option value="${u}">${u}</option>`);
}

function setupDragAndDrop(project) {
    const tasks = document.querySelectorAll('.task');
    const columns = document.querySelectorAll('.col');

    tasks.forEach(task => {
        task.addEventListener('dragstart', () => task.classList.add('dragging'));
        task.addEventListener('dragend', () => task.classList.remove('dragging'));
    });

    columns.forEach(col => {
        col.addEventListener('dragover', e => { e.preventDefault(); col.classList.add('drag-over'); });
        col.addEventListener('dragleave', () => col.classList.remove('drag-over'));
        col.addEventListener('drop', e => {
            e.preventDefault();
            col.classList.remove('drag-over');
            const draggable = document.querySelector('.dragging');
            if(draggable) {
                const newStatus = col.getAttribute('data-status');
                const taskId = parseInt(draggable.getAttribute('data-id'));
                let taskData = project.tasks.find(t => t.id === taskId);
                if(taskData && taskData.status !== newStatus) {
                    taskData.status = newStatus;
                    showToast('Görev durumu güncellendi.');
                    renderAdminBoard(project); 
                }
            }
        });
    });
}

function addTeamMember() {
    let newMember = document.getElementById('newTeamMember').value;
    let project = projects.find(p => p.admin === activeUser);
    if(project && newMember) {
        project.team.push(newMember);
        closeModal('teamModal');
        renderAdminBoard(project);
        showToast(`${newMember} takıma eklendi.`);
    }
}

function createTask() {
    let title = document.getElementById('newTaskTitle').value;
    let assignee = document.getElementById('taskAssignee').value;
    let project = projects.find(p => p.admin === activeUser);
    
    if(project && title && assignee) {
        project.tasks.push({ id: Date.now(), title: title, assignee: assignee, status: 'todo' });
        closeModal('taskModal');
        document.getElementById('newTaskTitle').value = '';
        renderAdminBoard(project);
        showToast('Yeni görev atandı.');
    } else {
        showToast('Lütfen önce takıma üye ekleyin.', 'error');
    }
}

// --- LOGLAR (ADMİN İÇİN) ---
function renderAdminInbox(project) {
    if(!project) return;
    let container = document.getElementById('adminInboxList');
    container.innerHTML = '';
    if(project.logs.length === 0) return container.innerHTML = '<p style="color: #94a3b8; font-weight:600;">Henüz gelen bir bildirim yok.</p>';

    [...project.logs].reverse().forEach(log => {
        let badgeColor = log.newStatus === 'Tamamlandı' ? '#10b981' : (log.newStatus === 'Sorun Var' ? '#ef4444' : '#3b82f6');
        container.innerHTML += `
        <div class="log-card" style="background:white; padding:18px; border-radius:10px; border-left:5px solid #f59e0b; margin-bottom:15px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
            <div style="font-size:0.9rem; color:#94a3b8; margin-bottom:10px; display:flex; justify-content:space-between;">
                <span style="color:#1e293b;"><strong>${log.user}</strong> 👉 "${log.taskTitle}"</span><span>${log.time}</span>
            </div>
            <div style="margin-bottom:10px; font-size:0.85rem; font-weight:bold; color:${badgeColor};">Yeni Durum: ${log.newStatus}</div>
            <div style="background:#f8fafc; padding:15px; border-radius:8px; font-style:italic;">"${log.message}"</div>
        </div>`;
    });
}

// --- ÇALIŞAN İŞLEMLERİ ---
function renderEmployeeTasks() {
    document.getElementById('employeeTitle').innerText = activeUser + " - Görevlerim";
    let container = document.getElementById('employeeTasksList');
    container.innerHTML = '';
    let hasTasks = false;

    projects.forEach(project => {
        project.tasks.filter(t => t.assignee === activeUser).forEach(task => {
            hasTasks = true;
            let statusHtml = task.status === 'todo' ? '<span style="color:#3b82f6;">YAPILACAK</span>' : (task.status === 'progress' ? '<span style="color:#f59e0b;">DEVAM EDİYOR</span>' : (task.status === 'blocked' ? '<span style="color:#ef4444;">SORUN VAR</span>' : '<span style="color:#94a3b8;">TAMAMLANDI</span>'));

            container.innerHTML += `
            <div class="my-task-card" style="background:white; padding:20px; border-radius:10px; border-left:5px solid #3b82f6; margin-bottom:15px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); display:flex; justify-content:space-between;">
                <div>
                    <div style="font-size:0.75rem; color:#94a3b8; font-weight:700; text-transform:uppercase;">📁 ${project.name}</div>
                    <div style="font-size:1.2rem; font-weight:800; color:#1e293b; margin-bottom:8px;">${task.title}</div>
                    <div style="font-size:0.85rem; font-weight:600;">Durum: ${statusHtml}</div>
                </div>
                <button class="btn-primary" onclick="openStatusModal(${project.id}, ${task.id})">Durum Güncelle</button>
            </div>`;
        });
    });
    if(!hasTasks) container.innerHTML = '<p style="color: #94a3b8; font-weight:600;">Şu an bekleyen bir işiniz yok.</p>';
}

function openStatusModal(projectId, taskId) {
    currentStatusProjectId = projectId;
    currentStatusTaskId = taskId;
    openModal('statusModal');
}

function confirmStatusChange() {
    let newStatus = document.getElementById('statusSelect').value;
    let message = document.getElementById('statusMessage').value;
    if(message.trim() === '') return showToast("Açıklama zorunludur!", "error");

    let project = projects.find(p => p.id === currentStatusProjectId);
    let task = project.tasks.find(t => t.id === currentStatusTaskId);

    task.status = newStatus;
    let statusText = newStatus === 'done' ? 'Tamamlandı' : (newStatus === 'blocked' ? 'Sorun Var' : 'Devam Ediyor');
    
    project.logs.push({
        user: activeUser,
        taskTitle: task.title,
        newStatus: statusText,
        message: message,
        time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    });

    closeModal('statusModal');
    document.getElementById('statusMessage').value = '';
    showToast("Log başarıyla iletildi.");
    renderEmployeeTasks(); 
}

// Başlangıç
window.onload = switchUser;