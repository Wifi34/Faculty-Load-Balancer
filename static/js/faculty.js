/**
 * Faculty Directory & Profile Management Controller
 */
const FacultyManager = {
  allFaculty: [],

  async loadFacultyDirectory() {
    console.log('[FacultyManager] Loading faculty directory...');
    const container = document.getElementById('facultyDirectoryGrid');
    if (!container) return;

    container.innerHTML = '<div style="padding: 30px; text-align: center;">Loading faculty profiles...</div>';

    try {
      this.allFaculty = await API.getFaculty();
      this.renderFacultyCards(this.allFaculty);
    } catch (err) {
      container.innerHTML = `<div class="conflict-banner conflict-danger">Failed to load faculty: ${err.message}</div>`;
    }
  },

  renderFacultyCards(list) {
    const container = document.getElementById('facultyDirectoryGrid');
    if (!container) return;

    if (!list.length) {
      container.innerHTML = '<div style="padding: 30px; text-align: center; color: #64748b;">No faculty profiles found.</div>';
      return;
    }

    container.innerHTML = list.map(f => {
      let statusBadge = '<span class="badge badge-balanced">Balanced Load</span>';
      if (f.workload_status === 'High') {
        statusBadge = '<span class="badge badge-high">High Load</span>';
      } else if (f.workload_status === 'Low') {
        statusBadge = '<span class="badge badge-low">Low Load (Available)</span>';
      }

      return `
        <div class="card" style="margin-bottom: 0; display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
              <div>
                <h3 style="font-size: 15px; font-weight: 700; color: #0f172a;">${f.name}</h3>
                <div style="font-size: 12px; color: #2563eb; font-weight: 600;">${f.designation}</div>
                <div style="font-size: 11px; color: #64748b;">${f.faculty_code} • ${f.department}</div>
              </div>
              ${statusBadge}
            </div>

            <div style="background: #f8fafc; border-radius: 8px; padding: 10px 12px; margin-bottom: 14px; font-size: 12px;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">Current Weekly Load:</span>
                <strong>${f.total_load_hours} / ${f.weekly_lecture_limit} hrs</strong>
              </div>
              <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                <span style="color: #64748b;">Lectures & Labs:</span>
                <span>${f.weekly_lectures} sessions</span>
              </div>
              <div style="display: flex; justify-content: space-between;">
                <span style="color: #64748b;">Assigned Duties:</span>
                <span>${f.assigned_duties} duties</span>
              </div>
            </div>

            <div style="font-size: 12px; color: #334155; margin-bottom: 14px;">
              <div style="margin-bottom: 3px;">📧 <a href="mailto:${f.email}" style="color: #2563eb; text-decoration: none;">${f.email}</a></div>
              <div style="margin-bottom: 3px;">📞 ${f.phone || 'N/A'}</div>
              <div>📍 ${f.cabin_room || 'Main Block'}</div>
            </div>

            <div style="font-size: 11.5px; color: #64748b; margin-bottom: 16px;">
              <strong>Subjects:</strong> ${f.subjects_taught || 'General Computing'}
            </div>
          </div>

          <div style="border-top: 1px solid #f1f5f9; padding-top: 12px; display: flex; justify-content: space-between; align-items: center;">
            <button class="btn btn-sm btn-outline-primary" onclick="Assignments.openAssignmentModal(${f.id})">
              ➕ Assign
            </button>
            <div style="display: flex; gap: 6px;">
              <button class="btn btn-sm btn-secondary" onclick="Timetable.viewSpecificFacultyTimetable(${f.id})">
                📅 Timetable
              </button>
              ${App.currentUser.role === 'hod' ? `
                <button class="btn btn-sm btn-secondary" onclick="FacultyManager.openEditModal(${f.id})" title="Edit Profile">
                  ✏️
                </button>
              ` : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  filterFacultyDirectory() {
    const q = (document.getElementById('directorySearchInput')?.value || '').toLowerCase();
    const filtered = this.allFaculty.filter(f => {
      return !q || f.name.toLowerCase().includes(q) || f.faculty_code.toLowerCase().includes(q) || f.designation.toLowerCase().includes(q) || (f.subjects_taught && f.subjects_taught.toLowerCase().includes(q));
    });
    this.renderFacultyCards(filtered);
  },

  openAddModal() {
    const form = document.getElementById('addFacultyForm');
    if (form) form.reset();
    document.getElementById('addFacultyModal')?.classList.add('show');
  },

  async handleAddFaculty(e) {
    e.preventDefault();
    const payload = {
      faculty_code: document.getElementById('newFacCode').value.trim(),
      name: document.getElementById('newFacName').value.trim(),
      department: document.getElementById('newFacDept').value.trim(),
      designation: document.getElementById('newFacDesignation').value.trim(),
      email: document.getElementById('newFacEmail').value.trim(),
      phone: document.getElementById('newFacPhone').value.trim(),
      cabin_room: document.getElementById('newFacCabin').value.trim(),
      subjects_taught: document.getElementById('newFacSubjects').value.trim(),
      weekly_lecture_limit: parseInt(document.getElementById('newFacLimit').value || 16, 10),
      max_duties_limit: 6,
      is_active: true
    };

    try {
      const res = await API.createFaculty(payload);
      App.toast(`Faculty ${payload.name} created! Default login: ${res.default_username} / faculty123`, 'success');
      document.getElementById('addFacultyModal')?.classList.remove('show');
      this.loadFacultyDirectory();
      Dashboard.loadHodDashboard();
    } catch (err) {
      App.toast(`Failed to create faculty: ${err.message}`, 'danger');
    }
  },

  async openEditModal(facultyId) {
    try {
      const data = await API.getFacultyById(facultyId);
      const f = data.faculty;

      document.getElementById('editFacId').value = f.id;
      document.getElementById('editFacName').value = f.name;
      document.getElementById('editFacDesignation').value = f.designation;
      document.getElementById('editFacEmail').value = f.email;
      document.getElementById('editFacPhone').value = f.phone || '';
      document.getElementById('editFacCabin').value = f.cabin_room || '';
      document.getElementById('editFacSubjects').value = f.subjects_taught || '';
      document.getElementById('editFacLimit').value = f.weekly_lecture_limit;

      document.getElementById('editFacultyModal')?.classList.add('show');
    } catch (err) {
      App.toast(`Could not load faculty details: ${err.message}`, 'danger');
    }
  },

  async handleEditFaculty(e) {
    e.preventDefault();
    const id = document.getElementById('editFacId').value;
    const payload = {
      name: document.getElementById('editFacName').value.trim(),
      designation: document.getElementById('editFacDesignation').value.trim(),
      email: document.getElementById('editFacEmail').value.trim(),
      phone: document.getElementById('editFacPhone').value.trim(),
      cabin_room: document.getElementById('editFacCabin').value.trim(),
      subjects_taught: document.getElementById('editFacSubjects').value.trim(),
      weekly_lecture_limit: parseInt(document.getElementById('editFacLimit').value, 10)
    };

    try {
      await API.updateFaculty(id, payload);
      App.toast('Faculty profile updated successfully!', 'success');
      document.getElementById('editFacultyModal')?.classList.remove('show');
      this.loadFacultyDirectory();
      Dashboard.loadHodDashboard();
    } catch (err) {
      App.toast(`Failed to update faculty: ${err.message}`, 'danger');
    }
  }
};

window.FacultyManager = FacultyManager;
