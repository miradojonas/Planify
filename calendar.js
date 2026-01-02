// Gestion du calendrier
class CalendarManager {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            defaultView: 'month',
            ...options
        };
        this.currentDate = new Date();
        this.events = [];
        
        this.init();
    }
    
    init() {
        this.render();
        this.loadEvents();
        this.bindEvents();
    }
    
    render() {
        if (!this.container) return;
        
        const view = this.getCurrentView();
        switch (view) {
            case 'month':
                this.renderMonthView();
                break;
            case 'week':
                this.renderWeekView();
                break;
            case 'day':
                this.renderDayView();
                break;
        }
    }
    
    getCurrentView() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('view') || this.options.defaultView;
    }
    
    renderMonthView() {
        const today = new Date();
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const lastDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - startDate.getDay() + 1); // Lundi de la semaine
        
        const endDate = new Date(lastDay);
        endDate.setDate(endDate.getDate() + (6 - endDate.getDay())); // Dimanche de la semaine
        
        let html = `
            <div class="calendar-header">
                <div class="calendar-nav">
                    <button class="btn btn-outline btn-sm" onclick="calendar.prevMonth()">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <h2>${this.currentDate.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</h2>
                    <button class="btn btn-outline btn-sm" onclick="calendar.nextMonth()">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="calendar-views">
                    <button class="view-btn ${this.getCurrentView() === 'day' ? 'active' : ''}" onclick="calendar.switchView('day')">Jour</button>
                    <button class="view-btn ${this.getCurrentView() === 'week' ? 'active' : ''}" onclick="calendar.switchView('week')">Semaine</button>
                    <button class="view-btn ${this.getCurrentView() === 'month' ? 'active' : ''}" onclick="calendar.switchView('month')">Mois</button>
                </div>
            </div>
            <div class="calendar-grid month-view">
                <div class="calendar-weekdays">
                    ${['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map(day => `
                        <div class="calendar-weekday">${day}</div>
                    `).join('')}
                </div>
                <div class="calendar-days">
        `;
        
        const currentDate = new Date(startDate);
        while (currentDate <= endDate) {
            const isCurrentMonth = currentDate.getMonth() === this.currentDate.getMonth();
            const isToday = currentDate.toDateString() === today.toDateString();
            const dateString = currentDate.toISOString().split('T')[0];
            const dayEvents = this.events.filter(event => 
                event.start.startsWith(dateString)
            );
            
            html += `
                <div class="calendar-day ${!isCurrentMonth ? 'other-month' : ''} ${isToday ? 'today' : ''}">
                    <div class="day-number">${currentDate.getDate()}</div>
                    <div class="day-events">
                        ${dayEvents.slice(0, 3).map(event => `
                            <div class="calendar-event" style="background: ${event.color}" 
                                 onclick="calendar.openEvent(${event.id})">
                                ${event.title}
                            </div>
                        `).join('')}
                        ${dayEvents.length > 3 ? `
                            <div class="more-events">+${dayEvents.length - 3} plus</div>
                        ` : ''}
                    </div>
                </div>
            `;
            
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        html += `</div></div>`;
        this.container.innerHTML = html;
    }
    
    renderWeekView() {
        // Implémentation simplifiée de la vue semaine
        this.container.innerHTML = `
            <div class="calendar-header">
                <h2>Vue Semaine - En développement</h2>
                <button class="btn btn-primary" onclick="calendar.switchView('month')">
                    Retour au mois
                </button>
            </div>
        `;
    }
    
    renderDayView() {
        // Implémentation simplifiée de la vue jour
        this.container.innerHTML = `
            <div class="calendar-header">
                <h2>Vue Jour - En développement</h2>
                <button class="btn btn-primary" onclick="calendar.switchView('month')">
                    Retour au mois
                </button>
            </div>
        `;
    }
    
    async loadEvents() {
        try {
            const startDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
            const endDate = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0);
            
            const response = await fetch(`/api/events?start=${startDate.toISOString()}&end=${endDate.toISOString()}`);
            this.events = await response.json();
            this.render();
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }
    
    prevMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.loadEvents();
    }
    
    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.loadEvents();
    }
    
    switchView(view) {
        const url = new URL(window.location);
        url.searchParams.set('view', view);
        window.location.href = url.toString();
    }
    
    openEvent(eventId) {
        window.location.href = `/event/${eventId}`;
    }
    
    bindEvents() {
        // Bind keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                this.prevMonth();
            } else if (e.key === 'ArrowRight') {
                this.nextMonth();
            }
        });
    }
}

// Initialisation du calendrier
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('calendar')) {
        window.calendar = new CalendarManager('calendar');
    }
});

// Gestion des formulaires d'événements
function initEventForm() {
    const form = document.getElementById('eventForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const eventData = {
                title: formData.get('title'),
                description: formData.get('description'),
                start_date: formData.get('start_date'),
                end_date: formData.get('end_date'),
                color: formData.get('color'),
                location: formData.get('location'),
                event_type: formData.get('event_type')
            };
            
            try {
                const response = await fetch('/api/events', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(eventData)
                });
                
                if (response.ok) {
                    Plinify.showNotification('Événement créé avec succès');
                    setTimeout(() => {
                        window.location.href = '/calendar';
                    }, 1000);
                } else {
                    throw new Error('Erreur lors de la création');
                }
            } catch (error) {
                console.error('Error:', error);
                Plinify.showNotification('Erreur lors de la création de l\'événement', 'error');
            }
        });
        
        // Initialisation du datetime picker
        const dateInputs = form.querySelectorAll('input[type="datetime-local"]');
        dateInputs.forEach(input => {
            if (!input.value) {
                const now = new Date();
                now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
                input.value = now.toISOString().slice(0, 16);
            }
        });
    }
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', function() {
    initEventForm();
});