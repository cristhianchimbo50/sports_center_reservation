function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

function updateDayOfWeek() {
    const input = document.querySelector('input[name="selected_date"]');
    const output = document.getElementById('dayOfWeek');

    if (input.value) {
        const date = new Date(input.value + 'T00:00:00');
        const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
        output.value = days[date.getUTCDay()];
    } else {
        output.value = '';
    }
}

// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const courtSelect = document.getElementById('courtSelect');
    const dateSelect = document.getElementById('dateSelect');
    const timeSlotSelect = document.getElementById('timeSlotSelect');

    async function loadAvailableSlots() {
        const courtId = courtSelect.value;
        const date = dateSelect.value;

        if (!courtId || !date) {
            timeSlotSelect.innerHTML = '<option value="">Seleccione una fecha y cancha primero</option>';
            return;
        }

        const response = await fetch(`/api/available-slots?court_id=${courtId}&date=${date}`);
        const data = await response.json();

        if (data.available_slots && data.available_slots.length > 0) {
            timeSlotSelect.innerHTML = '';
            data.available_slots.forEach(slot => {
                const option = document.createElement('option');
                option.value = slot;
                option.textContent = slot;
                timeSlotSelect.appendChild(option);
            });
        } else {
            timeSlotSelect.innerHTML = '<option value="">No hay horarios disponibles</option>';
        }
    }

    courtSelect.addEventListener('change', loadAvailableSlots);
    dateSelect.addEventListener('change', loadAvailableSlots);
});

// scripts.js

document.addEventListener('DOMContentLoaded', function() {
    const courtSelect = document.getElementById('courtSelect');
    const dateSelect = document.getElementById('dateSelect');
    const slotsContainer = document.getElementById('slotsContainer');

    async function loadAvailableHours() {
        slotsContainer.innerHTML = '';
        const courtId = courtSelect.value;
        const date = dateSelect.value;

        if (!courtId || !date) {
            slotsContainer.innerHTML = '<span class="text-muted">Seleccione una cancha y una fecha.</span>';
            return;
        }

        const response = await fetch(`/api/available-hours?court_id=${courtId}&date=${date}`);
        const data = await response.json();

        if (data.hours && data.hours.length > 0) {
            data.hours.forEach(h => {
                const id = `slot_${h.slot.replace(/[:\-]/g, '')}`;
                let html = '';
                if (h.available) {
                    html = `
                        <div>
                            <input type="checkbox" class="btn-check" name="slots" id="${id}" autocomplete="off" value="${h.slot}">
                            <label class="btn btn-outline-success" for="${id}">${h.slot}</label>
                        </div>
                    `;
                } else {
                    html = `
                        <div>
                            <input type="checkbox" class="btn-check" disabled id="${id}">
                            <label class="btn btn-outline-danger disabled" for="${id}">${h.slot}</label>
                        </div>
                    `;
                }
                slotsContainer.insertAdjacentHTML('beforeend', html);
            });
        } else {
            slotsContainer.innerHTML = '<span class="text-danger">No hay horarios disponibles para este día.</span>';
        }
    }

    courtSelect.addEventListener('change', loadAvailableHours);
    dateSelect.addEventListener('change', loadAvailableHours);
});
