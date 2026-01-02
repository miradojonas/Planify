// Gestion de l'Emploi du Temps
class EDTManager {
    constructor() {
        this.schedule = {};
        this.currentWeek = new Date();
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadSchedule();
    }
    
    bindEvents() {
        // Navigation semaine
        const prevWeekBtn = document.getElementById('prevWeek');
        const nextWeekBtn = document.getElementById('nextWeek');
        const todayBtn = document.getElementById('today');
        
        if (prevWeekBtn) {
            prevWeekBtn.addEventListener('click', () => this.previousWeek());
        }
        if (nextWeekBtn) {
            nextWeekBtn.addEventListener('click', () => this.nextWeek());
        }
        if (todayBtn) {
            todayBtn.addEventListener('click', () => this.goToToday());
        }
        
        // Filtres
        const filters = document.querySelectorAll('.edt-filter');
        filters.forEach(filter => {
            filter.addEventListener('change', () => this.applyFilters());
        });
    }
    
    async loadSchedule() {
        try {
            // Pour l'instant, on utilise les données du template
            // Plus tard, on pourra faire un appel API
            this.schedule = window.scheduleData || {};
            this.renderSchedule();
        } catch (error) {
            console.error('Error loading schedule:', error);
            if (window.Plinify) {
                window.Plinify.showNotification('Erreur lors du chargement de l\'EDT', 'error');
            }
        }
    }
    
    renderSchedule() {
        const container = document.getElementById('edtGrid');
        if (!container) return;
        
        const days = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
        const timeSlots = [
            '08:00-09:30', '09:45-11:15', '11:30-13:00',
            '14:00-15:30', '15:45-17:15', '17:30-19:00'
        ];
        
        let html = '';
        
        // En-tête des jours
        html += '<div class="edt-time-header"></div>';
        days.forEach(day => {
            html += `<div class="edt-day-header">${day}</div>`;
        });
        
        // Lignes des créneaux horaires
        timeSlots.forEach(timeSlot => {
            html += `<div class="edt-time-slot">${timeSlot}</div>`;
            
            days.forEach(day => {
                const courses = this.schedule[day]?.[timeSlot] || [];
                html += `
                    <div class="edt-cell">
                        ${courses.map(course => `
                            <div class="course-slot" 
                                 style="border-left-color: ${course.color}; background: linear-gradient(135deg, ${course.color}15, ${course.color}25);"
                                 onclick="window.edtManager.openCourse(${course.id})">
                                <div class="course-name">${course.name}</div>
                                <div class="course-info">
                                    <span class="professor">${course.teacher?.prenom || course.professor}</span>
                                    <span class="classroom">${course.classroom?.name || course.salle}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            });
        });
        
        container.innerHTML = html;
        this.updateWeekDisplay();
    }
    
    previousWeek() {
        this.currentWeek.setDate(this.currentWeek.getDate() - 7);
        this.loadSchedule();
    }
    
    nextWeek() {
        this.currentWeek.setDate(this.currentWeek.getDate() + 7);
        this.loadSchedule();
    }
    
    goToToday() {
        this.currentWeek = new Date();
        this.loadSchedule();
    }
    
    updateWeekDisplay() {
        const weekDisplay = document.getElementById('currentWeek');
        if (weekDisplay) {
            const startOfWeek = new Date(this.currentWeek);
            startOfWeek.setDate(startOfWeek.getDate() - startOfWeek.getDay() + 1);
            
            const endOfWeek = new Date(startOfWeek);
            endOfWeek.setDate(endOfWeek.getDate() + 6);
            
            weekDisplay.textContent = 
                `Semaine du ${startOfWeek.toLocaleDateString('fr-FR')} au ${endOfWeek.toLocaleDateString('fr-FR')}`;
        }
    }
    
    applyFilters() {
        // Appliquer les filtres (professeur, salle, matière)
        const professorFilter = document.getElementById('professorFilter')?.value;
        const classroomFilter = document.getElementById('classroomFilter')?.value;
        const subjectFilter = document.getElementById('subjectFilter')?.value;
        
        const courseSlots = document.querySelectorAll('.course-slot');
        courseSlots.forEach(slot => {
            const professor = slot.querySelector('.professor')?.textContent;
            const classroom = slot.querySelector('.classroom')?.textContent;
            const courseName = slot.querySelector('.course-name')?.textContent;
            
            let show = true;
            
            if (professorFilter && professorFilter !== 'all' && professor !== professorFilter) {
                show = false;
            }
            if (classroomFilter && classroomFilter !== 'all' && classroom !== classroomFilter) {
                show = false;
            }
            if (subjectFilter && subjectFilter !== 'all' && !courseName?.toLowerCase().includes(subjectFilter.toLowerCase())) {
                show = false;
            }
            
            slot.style.display = show ? 'block' : 'none';
        });
    }
    
    openCourse(courseId) {
        // Ouvrir les détails du cours
        console.log('Opening course:', courseId);
        // window.location.href = `/course/${courseId}`;
        if (window.Plinify) {
            window.Plinify.showNotification('Détails du cours - Fonctionnalité en développement');
        }
    }
    
    exportSchedule(format = 'pdf') {
        // Exporter l'EDT
        switch (format) {
            case 'pdf':
                this.exportToPDF();
                break;
            case 'ical':
                this.exportToICal();
                break;
            case 'image':
                this.exportToImage();
                break;
        }
    }
    
    exportToPDF() {
        if (window.Plinify) {
            window.Plinify.showNotification('Export PDF en cours de développement');
        }
    }
    
    exportToICal() {
        if (window.Plinify) {
            window.Plinify.showNotification('Export iCal en cours de développement');
        }
    }
    
    exportToImage() {
        if (window.Plinify) {
            window.Plinify.showNotification('Export image en cours de développement');
        }
    }
}

// Gestion des salles
class ClassroomManager {
    constructor() {
        this.classrooms = [];
        this.init();
    }
    
    async init() {
        await this.loadClassrooms();
        this.bindEvents();
    }
    
    async loadClassrooms() {
        try {
            // Utiliser les données du template
            this.classrooms = window.classroomsData || [];
            this.renderClassrooms();
        } catch (error) {
            console.error('Error loading classrooms:', error);
        }
    }
    
    renderClassrooms() {
        const container = document.getElementById('classroomsGrid');
        if (!container) return;
        
        let html = '';
        
        this.classrooms.forEach(classroom => {
            html += `
                <div class="classroom-card">
                    <div class="classroom-header">
                        <h3>${classroom.name}</h3>
                        <span class="capacity-badge">${classroom.capacity} places</span>
                    </div>
                    <div class="classroom-info">
                        <p><strong>Localisation:</strong> ${classroom.location || 'Non spécifiée'}</p>
                        <p><strong>Équipement:</strong> ${classroom.equipment || 'Aucun équipement spécifique'}</p>
                        <p><strong>Statut:</strong> 
                            <span class="status-badge status-${classroom.is_active ? 'active' : 'inactive'}">
                                ${classroom.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </p>
                    </div>
                    <div class="classroom-actions">
                        <button class="btn btn-outline btn-sm" onclick="window.classroomManager.viewSchedule(${classroom.id})">
                            <i class="fas fa-eye"></i>
                            Voir planning
                        </button>
                        ${window.currentUserIsAdmin ? `
                            <button class="btn btn-outline btn-sm" onclick="window.classroomManager.editClassroom(${classroom.id})">
                                <i class="fas fa-edit"></i>
                                Modifier
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    viewSchedule(classroomId) {
        // Afficher le planning de la salle
        console.log('View schedule for classroom:', classroomId);
        if (window.Plinify) {
            window.Plinify.showNotification('Planning de la salle - Fonctionnalité en développement');
        }
    }
    
    editClassroom(classroomId) {
        // Ouvrir le formulaire d'édition
        console.log('Edit classroom:', classroomId);
        if (window.Plinify) {
            window.Plinify.showNotification('Édition de salle - Fonctionnalité en développement');
        }
    }
    
    async createClassroom(formData) {
        try {
            const response = await fetch('/api/classrooms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                if (window.Plinify) {
                    window.Plinify.showNotification('Salle créée avec succès');
                }
                this.loadClassrooms();
                if (window.Plinify) {
                    window.Plinify.closeModal('createClassroomModal');
                }
            } else {
                throw new Error('Erreur lors de la création');
            }
        } catch (error) {
            console.error('Error creating classroom:', error);
            if (window.Plinify) {
                window.Plinify.showNotification('Erreur lors de la création de la salle', 'error');
            }
        }
    }
    
    bindEvents() {
        // Gestion du formulaire de création
        const createForm = document.getElementById('createClassroomForm');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(createForm);
                this.createClassroom(Object.fromEntries(formData));
            });
        }
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    // Définir les variables globales depuis le template
    window.currentUserIsAdmin = typeof currentUserIsAdmin !== 'undefined' ? currentUserIsAdmin : false;
    window.scheduleData = typeof scheduleData !== 'undefined' ? scheduleData : {};
    window.classroomsData = typeof classroomsData !== 'undefined' ? classroomsData : [];
    
    // Initialiser l'EDT
    if (document.getElementById('edtGrid')) {
        window.edtManager = new EDTManager();
    }
    
    // Initialiser la gestion des salles
    if (document.getElementById('classroomsGrid')) {
        window.classroomManager = new ClassroomManager();
    }
});

// Fonctions globales pour l'export
function exportEDT(format) {
    if (window.edtManager) {
        window.edtManager.exportSchedule(format);
    }
}

function openClassroomSchedule(classroomId) {
    if (window.classroomManager) {
        window.classroomManager.viewSchedule(classroomId);
    }
}