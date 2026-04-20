// js/model.js

const Database = {
    users: [
        { id: 1, name: 'Admin', role: 'yonetici' },
        { id: 2, name: 'Ahmet Yılmaz', role: 'padmin' },
        { id: 3, name: 'Ali Berk', role: 'calisan' },
        { id: 4, name: 'Ayşe Kaya', role: 'calisan' }
    ],
    
    projects: [
        {
            id: 1,
            name: 'Django Backend Mimarisinin Kurulumu',
            admin: 'Ahmet Yılmaz',
            team: ['Ali Berk'],
            tasks: [
                { id: 101, title: 'Modellerin Oluşturulması', assignee: 'Ali Berk', status: 'todo' }
            ],
            logs: []
        }
    ],

    activeUser: 'Ahmet Yılmaz',

    // --- Veri Manipülasyon Metotları (ORM Simülasyonu) ---
    getActiveUserObj: function() {
        return this.users.find(u => u.name === this.activeUser);
    },

    createNewProject: function(name, adminName) {
        this.projects.push({
            id: Date.now(), name: name, admin: adminName, team: [], tasks: [], logs: []
        });
    },

    updateTaskStatus: function(projectId, taskId, newStatus, message) {
        let project = this.projects.find(p => p.id === projectId);
        let task = project.tasks.find(t => t.id === taskId);
        
        task.status = newStatus;
        
        project.logs.push({
            user: this.activeUser,
            taskTitle: task.title,
            newStatus: newStatus,
            message: message,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        });
    }
};