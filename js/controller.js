// js/controller.js

// Sayfa yüklendiğinde çalışacak ana kontroller
document.addEventListener('DOMContentLoaded', () => {
    // MVC'de Controller, URL'e göre hangi sayfanın (View) yükleneceğine karar verir.
    // Biz burada simülasyon amaçlı tüm view'ları index.html içine include ediyoruz.
    initNavigation();
});

function initNavigation() {
    const userRole = Database.getActiveUserObj().role;
    
    if(userRole === 'yonetici') {
        loadView('yonetici');
    } else if(userRole === 'padmin') {
        loadView('pano');
    } else {
        loadView('islerim');
    }
}

function loadView(viewName) {
    // Ekrandaki tüm view div'lerini gizle
    document.querySelectorAll('.view-page').forEach(page => page.style.display = 'none');
    
    // İstenen view'ı göster (Bu aslında Django'da render(request, 'template.html') mantığıdır)
    document.getElementById(`view-${viewName}`).style.display = 'flex';

    // View yüklendiğinde içine verileri (Context) bas
    if(viewName === 'yonetici') {
        bindManagerData();
    } else if(viewName === 'pano') {
        bindBoardData();
    }
}

// Modelden (Database) veriyi alıp, View'a (HTML) bağlama işlemleri
function bindManagerData() {
    const list = document.getElementById('managerProjectsList');
    list.innerHTML = '';
    Database.projects.forEach(p => {
        list.innerHTML += `<div class="card"><h3>${p.name}</h3><p>👑 Admin: ${p.admin}</p></div>`;
    });
}

function bindBoardData() {
    // Kanban panosunu Database.projects verisine göre çizer (Sürükle bırak dahil)
    // (Önceki kodumuzdaki renderAdminBoard fonksiyonunun içeriği buraya gelir)
}

// UI Aksiyonları (Event Listeners)
function handleCreateProject() {
    let name = document.getElementById('newProjName').value;
    let admin = document.getElementById('newProjAdmin').value;
    
    Database.createNewProject(name, admin); // Modele kaydet
    bindManagerData(); // View'ı güncelle
}