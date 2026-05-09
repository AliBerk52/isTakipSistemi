// Sayfa Yönlendirme
function goTo(page) {
    window.location.href = page;
}

// Proje Verileri (Simülasyon)
const mockData = {
    projects: JSON.parse(localStorage.getItem('projects')) || [
        { id: 1, name: "E-Ticaret Paneli", admin: "Ahmet", status: "Devam Ediyor", team: ["Ali", "Ayşe"] }
    ],
    tasks: JSON.parse(localStorage.getItem('tasks')) || [
        { id: 1, projectId: 1, title: "Veritabanı Tasarımı", assignedTo: "Ali", status: "todo", logs: [] }
    ]
};

// Veriyi Kaydet
function saveData() {
    localStorage.setItem('projects', JSON.stringify(mockData.projects));
    localStorage.setItem('tasks', JSON.stringify(mockData.tasks));
}