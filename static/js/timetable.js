/**
 * Weekly Timetable Matrix Controller (Monday to Saturday)
 * Role-Based: HOD can view any faculty; Faculty sees only their own timetable
 */
const Timetable = {
  activeFacultyFilter: null,
  activeClassroomFilter: null,
  activeSubjectFilter: null,

  TIME_SLOTS: [
    { start: '09:00', end: '10:00', label: '09:00 - 10:00' },
    { start: '10:00', end: '11:00', label: '10:00 - 11:00' },
    { start: '11:00', end: '12:00', label: '11:00 - 12:00' },
    { start: '12:00', end: '13:00', label: '12:00 - 01:00' },
    { start: '13:00', end: '14:00', label: '01:00 - 02:00 (Lunch)', isBreak: true },
    { start: '14:00', end: '15:00', label: '02:00 - 03:00' },
    { start: '15:00', end: '16:00', label: '03:00 - 04:00' },
    { start: '16:00', end: '17:00', label: '04:00 - 05:00' },
  ],

  DAYS: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],

  async initFilters() {
    const isHod = App.currentUser && App.currentUser.role === 'hod';
    const facSelect = document.getElementById('timetableFacultySelect');
    const roomSelect = document.getElementById('timetableRoomSelect');
    const subjSelect = document.getElementById('timetableSubjectSelect');

    if (facSelect) {
      if (isHod) {
        facSelect.disabled = false;
        try {
          const faculty = await API.getFaculty();
          facSelect.innerHTML = '<option value="">All Faculty Members</option>' +
            faculty.map(f => `<option value="${f.id}">${f.name} (${f.faculty_code})</option>`).join('');
          if (this.activeFacultyFilter) {
            facSelect.value = this.activeFacultyFilter;
          }
        } catch (err) {
          console.warn('Could not populate faculty filter:', err);
        }
      } else {
        // Faculty: locked to self
        facSelect.innerHTML = `<option value="${App.currentUser.faculty_id}">${App.currentUser.full_name}</option>`;
        facSelect.disabled = true;
      }
    }

    if (roomSelect && roomSelect.options.length <= 1) {
      try {
        const rooms = await API.getClassrooms();
        roomSelect.innerHTML = '<option value="">All Classrooms / Labs</option>' +
          rooms.map(r => `<option value="${r.id}">${r.room_no} (${r.room_type})</option>`).join('');
      } catch (e) { console.warn(e); }
    }

    if (subjSelect && subjSelect.options.length <= 1) {
      try {
        const subjects = await API.getSubjects();
        subjSelect.innerHTML = '<option value="">All Subjects</option>' +
          subjects.map(s => `<option value="${s.id}">${s.code}: ${s.name}</option>`).join('');
      } catch (e) { console.warn(e); }
    }
  },

  async loadTimetable() {
    console.log('[Timetable] Loading weekly timetable grid...');
    await this.initFilters();

    const isHod = App.currentUser && App.currentUser.role === 'hod';
    const params = {};

    if (isHod) {
      const selectedFac = document.getElementById('timetableFacultySelect')?.value;
      if (selectedFac) params.faculty_id = selectedFac;
    }
    const selectedRoom = document.getElementById('timetableRoomSelect')?.value;
    if (selectedRoom) params.classroom_id = selectedRoom;
    const selectedSubj = document.getElementById('timetableSubjectSelect')?.value;
    if (selectedSubj) params.subject_id = selectedSubj;

    const gridContainer = document.getElementById('timetableGridContainer');
    if (!gridContainer) return;

    gridContainer.innerHTML = '<div style="padding: 30px; text-align: center;">Rendering timetable...</div>';

    try {
      const data = await API.getWeeklyTimetable(params);
      this.renderWeeklyMatrix(data.timetable);
    } catch (err) {
      gridContainer.innerHTML = `<div class="conflict-banner conflict-danger">Failed to load timetable: ${err.message}</div>`;
    }
  },

  renderWeeklyMatrix(timetableData) {
    const container = document.getElementById('timetableGridContainer');
    if (!container) return;

    let html = `
      <table class="timetable-table">
        <thead>
          <tr>
            <th style="width: 120px;">Day</th>
    `;

    // Header Time Slots
    this.TIME_SLOTS.forEach(slot => {
      html += `<th>${slot.label}</th>`;
    });
    html += `</tr></thead><tbody>`;

    // Days Rows (Monday to Saturday)
    this.DAYS.forEach(day => {
      const daySlots = timetableData[day] || [];

      html += `<tr>
        <td class="timetable-day-header">${day}</td>
      `;

      this.TIME_SLOTS.forEach(timeSlot => {
        if (timeSlot.isBreak) {
          html += `<td style="background: #f1f5f9; text-align: center; vertical-align: middle; color: #94a3b8; font-size: 11px; font-weight: 600;">LUNCH</td>`;
          return;
        }

        // Find schedules that overlap with this slot
        const matchingSchedules = daySlots.filter(s => {
          return this.isSlotMatching(s.start_time, s.end_time, timeSlot.start, timeSlot.end);
        });

        html += `<td>`;
        if (matchingSchedules.length > 0) {
          matchingSchedules.forEach(item => {
            let typeClass = 'slot-regular';
            if (item.schedule_type === 'substitute_lecture') typeClass = 'slot-substitute';
            else if (item.schedule_type === 'lab_duty') typeClass = 'slot-lab';
            else if (item.schedule_type === 'exam_duty') typeClass = 'slot-exam';
            else if (item.schedule_type === 'college_duty') typeClass = 'slot-college';

            html += `
              <div class="slot-item ${typeClass}" onclick="Timetable.showSlotDetails(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                <div class="slot-time">${item.start_time} - ${item.end_time}</div>
                <div class="slot-title">${item.duty_title}</div>
                <div class="slot-meta">
                  <span>📍 ${item.classroom}</span>
                </div>
                ${App.currentUser.role === 'hod' ? `<div class="slot-meta"><span>👨‍🏫 ${item.faculty_name}</span></div>` : ''}
              </div>
            `;
          });
        }
        html += `</td>`;
      });

      html += `</tr>`;
    });

    html += `</tbody></table>`;
    container.innerHTML = html;
  },

  isSlotMatching(sStart, sEnd, slotStart, slotEnd) {
    const toMin = (t) => {
      const [h, m] = t.split(':').map(Number);
      return h * 60 + m;
    };
    const s1 = toMin(sStart), e1 = toMin(sEnd);
    const s2 = toMin(slotStart), e2 = toMin(slotEnd);
    return Math.max(s1, s2) < Math.min(e1, e2);
  },

  viewSpecificFacultyTimetable(facultyId) {
    this.activeFacultyFilter = facultyId;
    App.showView('view-timetable');
    const select = document.getElementById('timetableFacultySelect');
    if (select) {
      select.value = facultyId;
      this.loadTimetable();
    }
  },

  showSlotDetails(slot) {
    const modal = document.getElementById('scheduleDetailsModal');
    if (!modal) return;

    document.getElementById('slotDetailTitle').textContent = slot.duty_title;
    document.getElementById('slotDetailType').textContent = slot.schedule_type.replace('_', ' ').toUpperCase();
    document.getElementById('slotDetailFaculty').textContent = slot.faculty_name || 'N/A';
    document.getElementById('slotDetailTime').textContent = `${slot.start_time} - ${slot.end_time} (${slot.duration_hours || 1} hrs)`;
    document.getElementById('slotDetailRoom').textContent = slot.classroom || 'N/A';
    document.getElementById('slotDetailClass').textContent = slot.class_name || 'N/A';
    document.getElementById('slotDetailDate').textContent = `${slot.date} (${slot.day_of_week || ''})`;
    document.getElementById('slotDetailInstructions').textContent = slot.instructions || 'No special instructions provided.';

    modal.classList.add('show');
  },

  printTimetable() {
    window.print();
  }
};

window.Timetable = Timetable;
