function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
}

// Actualiza el campo de día de la semana basado en la fecha seleccionada
function updateDayOfWeek() {
    const input = document.querySelector('input[name="selected_date"]');
    const output = document.getElementById('dayOfWeek');

    if (input && output) {
        if (input.value) {
            const date = new Date(input.value + 'T00:00:00');
            const days = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
            output.value = days[date.getUTCDay()];
        } else {
            output.value = '';
        }
    }
}

// --- Reserva: lógica de slots, precio, y pago (solo en add_reservation.html) ---
document.addEventListener('DOMContentLoaded', function() {
    const courtSelect = document.getElementById('courtSelect');
    const dateSelect = document.getElementById('dateSelect');
    const timeSlotSelect = document.getElementById('timeSlotSelect');

    // Solo aplica en formularios con selección simple de horario
    if (courtSelect && dateSelect && timeSlotSelect) {
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
    }

    // Horarios en formato checkboxes + cálculo de precio total (solo si los elementos existen)
    const slotsContainer = document.getElementById('slotsContainer');
    const pricePerHourSpan = document.getElementById('pricePerHour');
    const totalAmountSpan = document.getElementById('totalAmount');
    const openPaymentModalBtn = document.getElementById('openPaymentModal');
    const modalAmount = document.getElementById('modalAmount');
    let pricePerHour = 0;

    if (courtSelect && dateSelect && slotsContainer) {
        // Convierte un horario "HH:mm" a formato 12 horas
        function toAmPm(hhmm) {
            let [h, m] = hhmm.split(':').map(Number);
            const suffix = h >= 12 ? 'PM' : 'AM';
            h = ((h % 12) || 12);
            return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')} ${suffix}`;
        }
        // Convierte un slot "HH:mm-HH:mm" a formato legible
        function slotToAmPm(slot) {
            const [start, end] = slot.split('-');
            return `${toAmPm(start)} - ${toAmPm(end)}`;
        }

        // Consulta y muestra horarios disponibles para la cancha y fecha seleccionada
        async function loadAvailableHours() {
            slotsContainer.innerHTML = '';
            const courtId = courtSelect.value;
            const date = dateSelect.value;

            if (!courtId || !date) {
                slotsContainer.innerHTML = '<span class="text-muted">Seleccione una cancha y una fecha.</span>';
                updateTotal();
                return;
            }

            const response = await fetch(`/api/available-hours?court_id=${courtId}&date=${date}`);
            const data = await response.json();

            if (data.hours && data.hours.length > 0) {
                const shownSlots = new Set();
                let html = '<div class="row row-cols-2 row-cols-md-4 g-2 w-100">';
                data.hours.forEach(h => {
                    if (shownSlots.has(h.slot)) return;
                    shownSlots.add(h.slot);
                    const id = `slot_${h.slot.replace(/[:\-]/g, '')}`;
                    if (h.available) {
                        html += `
                            <div class="col">
                                <input type="checkbox" class="btn-check" name="slots" id="${id}" autocomplete="off" value="${h.slot}">
                                <label class="btn btn-outline-success w-100" for="${id}">${slotToAmPm(h.slot)}</label>
                            </div>
                        `;
                    } else {
                        html += `
                            <div class="col">
                                <input type="checkbox" class="btn-check" disabled id="${id}">
                                <label class="btn btn-outline-danger w-100 disabled" for="${id}">${slotToAmPm(h.slot)}</label>
                            </div>
                        `;
                    }
                });
                html += '</div>';
                slotsContainer.innerHTML = html;
            } else {
                slotsContainer.innerHTML = '<span class="text-danger">No hay horarios disponibles para este día.</span>';
            }
            updateTotal();
        }

        // Retorna el precio por hora según la cancha seleccionada
        function getCurrentPricePerHour() {
            const selected = courtSelect.selectedOptions[0];
            return selected && selected.dataset.price ? parseFloat(selected.dataset.price) : 0;
        }

        // Calcula y actualiza el total a pagar según horarios seleccionados
        function updateTotal() {
            pricePerHour = getCurrentPricePerHour();
            if (pricePerHourSpan) pricePerHourSpan.textContent = `$${pricePerHour.toFixed(2)}`;
            const checked = slotsContainer.querySelectorAll('input[type="checkbox"]:checked');
            const total = (checked.length * pricePerHour).toFixed(2);
            if (totalAmountSpan) totalAmountSpan.textContent = `$${total}`;
            if (modalAmount) modalAmount.value = `$${total}`;
            if (openPaymentModalBtn) openPaymentModalBtn.disabled = checked.length === 0 || pricePerHour === 0;
        }

        courtSelect.addEventListener('change', function() {
            updateTotal();
            loadAvailableHours();
        });
        dateSelect.addEventListener('change', loadAvailableHours);

        slotsContainer.addEventListener('change', updateTotal);

        if (openPaymentModalBtn) {
            openPaymentModalBtn.addEventListener('click', function() {
                const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
                modal.show();
            });
        }

        const paymentForm = document.getElementById('paymentForm');
        if (paymentForm) {
            paymentForm.addEventListener('submit', function(e) {
                e.preventDefault();
                document.getElementById('reservationForm').submit();
            });
        }

        updateTotal();
    }
});

// --- Detalle de reserva en modal usando datos globales renderizados por backend ---
window.RESERVAS = window.RESERVAS || [];

window.showReservaDetalle = function(reservaId) {
    reservaId = String(reservaId);
    const reserva = window.RESERVAS.find(r => String(r.id) === reservaId);
    const modalBody = document.getElementById('modalReservaBody');
    if (!reserva || !modalBody) {
        if (modalBody) modalBody.innerHTML = "<div class='text-danger'>No se encontró la reserva.</div>";
        return;
    }
    let html = `<div><strong>Fecha:</strong> ${reserva.date}</div>
                <div><strong>Cancha:</strong> ${reserva.court}</div>`;
    if (reserva.user) {
        html += `<div><strong>Usuario:</strong> ${reserva.user}</div>`;
    }
    html += `<div><strong>Horarios:</strong><ul>`;
    (reserva.horarios || []).forEach(h => {
        html += `<li>${h}</li>`;
    });
    html += `</ul></div>
             <div><strong>Estado:</strong> ${reserva.estado}</div>
             <div><strong>Pago:</strong> ${reserva.pago}</div>`;
    modalBody.innerHTML = html;
};
