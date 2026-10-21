/**
 * Lecture and Duty Assignment Controller
 * Features Real-Time Timetable Conflict Detection Engine
 */
const Assignments = {
  checkTimeout: null,
  lastConflictStatus: false,

  async initAssignmentForm() {
    console.log('[Assignments] Initializing assignment form...');
    await this.populateDropdowns();
    this.setupDateListeners();
    this.setupConflictListeners();
  },

  async populateDropdowns() {
    try {
      const [faculty, subjects, classes, rooms] = await Promise.all([
        API.getFaculty(),
        API.getSubjects(),
        API.getClasses(),
        API.getClassrooms()
      ]);

      const facSelect = document.getElementById('assignFacultySelect');
      const subjSelect = document.getElementById('assignSubjectSelect');
      const classSelect = document.getElementById('assignClassSelect');
      const roomSelect = document.getElementById('assignRoomSelect');

      if (facSelect) {
        facSelect.innerHTML = '<option value="">-- Select Faculty Member --</option>' +
          faculty.map(f => `<option value="${f.id}">${f.name} (${f.faculty_code} - ${f.workload_status} Load: ${f.total_load_hours}h)</option>`).join('');
      }

      if (subjSelect) {
        subjSelect.innerHTML = '<option value="">-- Select Subject (if applicable) --</option>' +
          subjects.map(s => `<option value="${s.id}">${s.code}: ${s.name}</option>`).join('');
      }

      if (classSelect) {
        classSelect.innerHTML = '<option value="">-- Select Class / Semester --</option>' +
          classes.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
      }

      if (roomSelect) {
        roomSelect.innerHTML = '<option value="">-- Select Classroom / Lab --</option>' +
          rooms.map(r => `<option value="${r.id}">${r.room_no} (${r.room_type})</option>`).join('');
      }

      // Default date to today
      const dateField = document.getElementById('assignDate');
      if (dateField && !dateField.value) {
        const today = new Date().toISOString().split('T')[0];
        dateField.value = today;
        this.updateDayOfWeek(today);
      }
    } catch (err) {
      console.error('Error populating assignment dropdowns:', err);
    }
  },

  setupDateListeners() {
    const dateField = document.getElementById('assignDate');
    if (dateField) {
      dateField.addEventListener('change', (e) => {
        this.updateDayOfWeek(e.target.value);
        this.triggerLiveConflictCheck();
      });
    }
  },

  updateDayOfWeek(dateStr) {
    if (!dateStr) return;
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const d = new Date(dateStr);
    const dayName = days[d.getDay()];
    const dayField = document.getElementById('assignDayOfWeek');
    if (dayField) {
      dayField.value = dayName;
    }
  },

  setupConflictListeners() {
    const triggers = ['assignFacultySelect', 'assignDate', 'assignStartTime', 'assignEndTime', 'assignRoomSelect', 'assignClassSelect'];
    triggers.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', () => this.triggerLiveConflictCheck());
        el.addEventListener('input', () => this.triggerLiveConflictCheck());
      }
    });
  },

  triggerLiveConflictCheck() {
    clearTimeout(this.checkTimeout);
    this.checkTimeout = setTimeout(() => this.runLiveConflictCheck(), 300);
  },

  async runLiveConflictCheck() {
    const facultyId = document.getElementById('assignFacultySelect')?.value;
    const date = document.getElementById('assignDate')?.value;
    const day = document.getElementById('assignDayOfWeek')?.value;
    const start = document.getElementById('assignStartTime')?.value;
    const end = document.getElementById('assignEndTime')?.value;
    const roomId = document.getElementById('assignRoomSelect')?.value;
    const banner = document.getElementById('liveConflictBanner');

    if (!banner) return;

    if (!facultyId || !date || !start || !end) {
      banner.style.display = 'none';
      return;
    }

    try {
      const res = await API.checkConflict({
        faculty_id: parseInt(facultyId, 10),
        date: date,
        day_of_week: day || 'Monday',
        start_time: start,
        end_time: end,
        classroom_id: roomId ? parseInt(roomId, 10) : null
      });

      this.lastConflictStatus = res.has_conflict;
      banner.style.display = 'flex';

      if (res.has_conflict) {
        banner.className = 'conflict-banner conflict-danger';
        banner.innerHTML = `
          <div class="conflict-icon">⚠️</div>
          <div>
            <strong>Schedule Conflict Detected!</strong>
            <div style="font-size: 12px; margin-top: 2px;">${res.message.replace(/\n/g, '<br/>')}</div>
          </div>
        `;
      } else {
        banner.className = 'conflict-banner conflict-success';
        banner.innerHTML = `
          <div class="conflict-icon">✓</div>
          <div>
            <strong>Slot Available</strong>
            <div style="font-size: 12px; margin-top: 2px;">Faculty and classroom are free of scheduling conflicts.</div>
          </div>
        `;
      }
    } catch (err) {
      console.warn('Conflict check request error:', err);
    }
  },

  async handleAssignmentSubmit(e) {
    e.preventDefault();
    const facultyId = document.getElementById('assignFacultySelect').value;
    const scheduleType = document.getElementById('assignScheduleType').value;
    const subjectId = document.getElementById('assignSubjectSelect').value;
    const classId = document.getElementById('assignClassSelect').value;
    const roomId = document.getElementById('assignRoomSelect').value;
    const date = document.getElementById('assignDate').value;
    const dayOfWeek = document.getElementById('assignDayOfWeek').value;
    const startTime = document.getElementById('assignStartTime').value;
    const endTime = document.getElementById('assignEndTime').value;
    const dutyTitle = document.getElementById('assignDutyTitle').value;
    const instructions = document.getElementById('assignInstructions').value;
    const reminderMinutes = document.getElementById('assignReminderMinutes').value;

    if (!facultyId || !date || !startTime || !endTime) {
      App.toast('Please fill all mandatory fields.', 'warning');
      return;
    }

    const payload = {
      schedule_type: scheduleType,
      faculty_id: parseInt(facultyId, 10),
      subject_id: subjectId ? parseInt(subjectId, 10) : null,
      class_id: classId ? parseInt(classId, 10) : null,
      classroom_id: roomId ? parseInt(roomId, 10) : null,
      day_of_week: dayOfWeek,
      date: date,
      start_time: startTime,
      end_time: endTime,
      duty_title: dutyTitle || null,
      instructions: instructions || null,
      reminder_minutes: parseInt(reminderMinutes || 15, 10)
    };

    const submitBtn = document.getElementById('assignSubmitBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Verifying & Assigning...';

    try {
      await API.createSchedule(payload, false);
      App.toast('Duty / Lecture assigned successfully! Faculty notified.', 'success');
      
      // Close modal if open
      document.getElementById('assignDutyModal')?.classList.remove('show');
      
      // Reset form
      document.getElementById('assignDutyForm')?.reset();
      document.getElementById('liveConflictBanner').style.display = 'none';

      // Refresh relevant views
      if (App.activeView === 'view-hod-dashboard') {
        Dashboard.loadHodDashboard();
      } else if (App.activeView === 'view-timetable') {
        Timetable.loadTimetable();
      } else {
        App.showView('view-hod-dashboard');
      }
    } catch (err) {
      if (err.detail && err.detail.conflict_details) {
        // Show conflict warning prompt
        const proceed = confirm(
          `Schedule Conflict Detected:\n\n${err.detail.conflict_details.message}\n\nDo you want to FORCE ASSIGN anyway?`
        );
        if (proceed) {
          try {
            await API.createSchedule(payload, true);
            App.toast('Duty force-assigned with administrator override.', 'warning');
            document.getElementById('assignDutyModal')?.classList.remove('show');
            Dashboard.loadHodDashboard();
          } catch (e2) {
            App.toast(`Failed to force assign: ${e2.message}`, 'danger');
          }
        }
      } else {
        App.toast(`Assignment failed: ${err.message}`, 'danger');
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Confirm & Assign Duty';
    }
  },

  openAssignmentModal(preselectFacultyId = null) {
    const modal = document.getElementById('assignDutyModal');
    if (!modal) return;

    this.initAssignmentForm().then(() => {
      if (preselectFacultyId) {
        const facSelect = document.getElementById('assignFacultySelect');
        if (facSelect) {
          facSelect.value = preselectFacultyId;
          this.triggerLiveConflictCheck();
        }
      }
      modal.classList.add('show');
    });
  }
};

window.Assignments = Assignments;
