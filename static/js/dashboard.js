/**
 * Dashboard & Workload Analytics Controller
 * Handles HOD Dashboard, Visual Charts, and Faculty Personal Dashboard
 */
const Dashboard = {
  facultyData: [],
  loadChart: null,
  doughnutChart: null,
  analyticsBarChart: null,

  async loadHodDashboard() {
    console.log('[Dashboard] Loading HOD Dashboard...');
    try {
      const summary = await API.getWorkloadSummary();
      this.facultyData = summary.faculty_list;

      this.renderKpiCards(summary);
      this.renderFacultyTable(this.facultyData);
      this.renderMiniWorkloadChart(summary.faculty_list);
      this.loadUpcomingEventsList();
    } catch (err) {
      console.error('Error loading HOD dashboard:', err);
      App.toast(`Failed to load dashboard data: ${err.message}`, 'danger');
    }
  },

  renderKpiCards(summary) {
    document.getElementById('kpiTotalFaculty').textContent = summary.total_faculty;
    document.getElementById('kpiTotalLectures').textContent = summary.total_lectures_scheduled;
    
    // Highest Load Faculty
    const highFac = summary.highest_load_faculty;
    if (highFac) {
      document.getElementById('kpiHighestLoad').textContent = `${highFac.total_load_hours} hrs`;
      document.getElementById('kpiHighestFacultyName').textContent = highFac.name;
    }

    // Lowest Load Faculty
    const lowFac = summary.lowest_load_faculty;
    if (lowFac) {
      document.getElementById('kpiLowestLoad').textContent = `${lowFac.total_load_hours} hrs`;
      document.getElementById('kpiLowestFacultyName').textContent = lowFac.name;
    }

    // Available for Extra duties
    document.getElementById('kpiAvailableFaculty').textContent = `${summary.available_faculty_count} Available`;
    document.getElementById('kpiAvgLoad').textContent = `${summary.average_teaching_load} hrs/wk avg`;
  },

  renderFacultyTable(list) {
    const tbody = document.getElementById('facultyWorkloadTableBody');
    if (!tbody) return;

    if (!list.length) {
      tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 24px;">No faculty records match your criteria.</td></tr>';
      return;
    }

    tbody.innerHTML = list.map(f => {
      let statusBadge = '';
      if (f.workload_status === 'High') {
        statusBadge = '<span class="badge badge-high">⚠️ High Load</span>';
      } else if (f.workload_status === 'Balanced') {
        statusBadge = '<span class="badge badge-balanced">✓ Balanced</span>';
      } else {
        statusBadge = '<span class="badge badge-low">⚡ Low Load (Available)</span>';
      }

      return `
        <tr>
          <td>
            <div class="faculty-meta-name">${f.name}</div>
            <div class="faculty-meta-code">${f.faculty_code} • ${f.designation}</div>
          </td>
          <td>${f.department}</td>
          <td style="max-width: 220px;" title="${f.subjects_taught || 'General'}">
            <small>${f.subjects_taught ? (f.subjects_taught.length > 40 ? f.subjects_taught.substring(0, 40) + '...' : f.subjects_taught) : 'Assigned'}</small>
          </td>
          <td style="text-align: center;"><strong>${f.weekly_lectures}</strong></td>
          <td style="text-align: center;"><span class="badge badge-regular">${f.assigned_duties}</span></td>
          <td>
            <strong>${f.total_load_hours} hrs</strong>
            <div style="font-size: 11px; color: #64748b;">Limit: ${f.weekly_lecture_limit} hrs</div>
            <div style="margin-top: 4px;">${statusBadge}</div>
          </td>
          <td>
            <span class="badge ${f.can_take_extra ? 'badge-balanced' : 'badge-high'}">
              ${f.available_slots} slots
            </span>
          </td>
          <td>
            <div class="actions-group">
              <button class="btn btn-sm btn-outline-primary" onclick="Assignments.openAssignmentModal(${f.faculty_id})" title="Assign lecture or duty">
                ➕ Assign
              </button>
              <button class="btn btn-sm btn-secondary" onclick="Timetable.viewSpecificFacultyTimetable(${f.faculty_id})" title="View weekly timetable">
                📅 Timetable
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  filterFacultyTable() {
    const q = (document.getElementById('facultySearchInput')?.value || '').toLowerCase();
    const statusFilter = document.getElementById('facultyStatusFilter')?.value || 'all';

    const filtered = this.facultyData.filter(f => {
      const matchQuery = !q || f.name.toLowerCase().includes(q) || f.faculty_code.toLowerCase().includes(q) || (f.subjects_taught && f.subjects_taught.toLowerCase().includes(q));
      const matchStatus = statusFilter === 'all' || f.workload_status.toLowerCase() === statusFilter.toLowerCase();
      return matchQuery && matchStatus;
    });

    this.renderFacultyTable(filtered);
  },

  renderMiniWorkloadChart(list) {
    const canvas = document.getElementById('dashboardWorkloadChart');
    if (!canvas || !window.Chart) return;

    if (this.loadChart) {
      this.loadChart.destroy();
    }

    const labels = list.map(f => f.name.replace('Dr. ', '').replace('Prof. ', ''));
    const loadHours = list.map(f => f.total_load_hours);
    const bgColors = list.map(f => f.workload_status === 'High' ? 'rgba(239, 68, 68, 0.85)' : (f.workload_status === 'Balanced' ? 'rgba(34, 197, 94, 0.85)' : 'rgba(59, 130, 246, 0.85)'));

    this.loadChart = new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total Load (Hours/Week)',
          data: loadHours,
          backgroundColor: bgColors,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterLabel: (context) => `Status: ${list[context.dataIndex].workload_status}`
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 22,
            title: { display: true, text: 'Hours / Week' }
          }
        }
      }
    });
  },

  async loadUpcomingEventsList() {
    const container = document.getElementById('dashboardUpcomingDuties');
    if (!container) return;

    try {
      const schedules = await API.getSchedules({ status_filter: 'scheduled' });
      // Take first 5 upcoming
      const slice = schedules.slice(0, 5);
      if (!slice.length) {
        container.innerHTML = '<div style="color: #64748b; font-size: 13px;">No upcoming duties scheduled.</div>';
        return;
      }

      container.innerHTML = slice.map(s => {
        let typeBadge = 'badge-regular';
        if (s.schedule_type === 'exam_duty') typeBadge = 'badge-exam';
        else if (s.schedule_type === 'substitute_lecture') typeBadge = 'badge-substitute';
        else if (s.schedule_type === 'lab_duty') typeBadge = 'badge-lab';
        else if (s.schedule_type === 'college_duty') typeBadge = 'badge-college';

        return `
          <div style="padding: 10px 12px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 600; font-size: 13px; color: #1e293b;">${s.duty_title}</div>
              <div style="font-size: 11.5px; color: #64748b;">
                👨‍🏫 ${s.faculty_name} • 📍 ${s.classroom_name || 'Designated Hall'} • 🕒 ${s.day_of_week}, ${s.start_time}-${s.end_time}
              </div>
            </div>
            <span class="badge ${typeBadge}">${s.schedule_type.replace('_', ' ').toUpperCase()}</span>
          </div>
        `;
      }).join('');
    } catch (err) {
      container.innerHTML = '<div style="color: #ef4444;">Could not load upcoming duties.</div>';
    }
  },

  // ------------------------------------------------------------------------
  // Dedicated Workload Analytics View
  // ------------------------------------------------------------------------
  async loadWorkloadAnalytics() {
    console.log('[Dashboard] Loading detailed workload comparison analytics...');
    try {
      const summary = await API.getWorkloadSummary();
      this.renderAnalyticsCharts(summary);
      this.renderAvailableFacultyList(summary.available_faculty);
    } catch (err) {
      App.toast(`Failed to load workload analytics: ${err.message}`, 'danger');
    }
  },

  renderAnalyticsCharts(summary) {
    const list = summary.faculty_list;

    // 1. Comparison Bar Chart
    const barCanvas = document.getElementById('analyticsComparisonChart');
    if (barCanvas && window.Chart) {
      if (this.analyticsBarChart) this.analyticsBarChart.destroy();

      this.analyticsBarChart = new Chart(barCanvas, {
        type: 'bar',
        data: {
          labels: list.map(f => f.name),
          datasets: [
            {
              label: 'Regular Lectures',
              data: list.map(f => f.regular_lectures),
              backgroundColor: '#3b82f6',
              borderRadius: 4
            },
            {
              label: 'Lab Sessions',
              data: list.map(f => f.lab_duties),
              backgroundColor: '#10b981',
              borderRadius: 4
            },
            {
              label: 'Substitute Lectures',
              data: list.map(f => f.substitute_lectures),
              backgroundColor: '#f59e0b',
              borderRadius: 4
            },
            {
              label: 'Exam & College Duties',
              data: list.map(f => f.assigned_duties),
              backgroundColor: '#8b5cf6',
              borderRadius: 4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { stacked: true },
            y: {
              stacked: true,
              beginAtZero: true,
              title: { display: true, text: 'Total Weekly Hours' }
            }
          }
        }
      });
    }

    // 2. Workload Breakdown Doughnut Chart
    const doughnutCanvas = document.getElementById('analyticsBreakdownChart');
    if (doughnutCanvas && window.Chart) {
      if (this.doughnutChart) this.doughnutChart.destroy();

      const bd = summary.workload_breakdown;
      this.doughnutChart = new Chart(doughnutCanvas, {
        type: 'doughnut',
        data: {
          labels: ['High Load (Overburdened)', 'Balanced Load (Optimal)', 'Low Load (Available)'],
          datasets: [{
            data: [bd.high, bd.balanced, bd.low],
            backgroundColor: ['#ef4444', '#22c55e', '#3b82f6'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom' }
          }
        }
      });
    }
  },

  renderAvailableFacultyList(availableList) {
    const container = document.getElementById('availableFacultyList');
    if (!container) return;

    if (!availableList || !availableList.length) {
      container.innerHTML = '<div class="alert alert-warning">All faculty members currently have balanced or high workloads.</div>';
      return;
    }

    container.innerHTML = availableList.map(f => `
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <div style="font-weight: 700; color: #1e293b;">${f.name} (${f.faculty_code})</div>
          <div style="font-size: 12px; color: #64748b;">
            Current Load: <strong>${f.total_load_hours} hrs</strong> / ${f.weekly_lecture_limit} hrs • <strong>${f.remaining_capacity} hrs remaining capacity</strong>
          </div>
          <div style="font-size: 11px; color: #475569; margin-top: 3px;">
            Subjects: ${f.subjects_taught || 'General'}
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="Assignments.openAssignmentModal(${f.faculty_id})">
          ➕ Assign Duty
        </button>
      </div>
    `).join('');
  },

  // ------------------------------------------------------------------------
  // Faculty Personal Dashboard
  // ------------------------------------------------------------------------
  async loadFacultyDashboard() {
    console.log('[Dashboard] Loading Faculty Personal Dashboard...');
    const user = App.currentUser;
    if (!user || !user.faculty_id) return;

    try {
      const data = await API.getFacultyById(user.faculty_id);
      const metrics = data.metrics;

      document.getElementById('facMyTotalLoad').textContent = `${metrics.total_load_hours} hrs`;
      document.getElementById('facMyLectureCount').textContent = metrics.weekly_lectures;
      document.getElementById('facMyDutyCount').textContent = metrics.assigned_duties;
      document.getElementById('facMyAvailableSlots').textContent = `${metrics.available_slots} slots`;

      // Progress bar
      const pct = Math.min(100, Math.round((metrics.total_load_hours / metrics.weekly_lecture_limit) * 100));
      const pBar = document.getElementById('facLoadProgressBar');
      if (pBar) {
        pBar.style.width = `${pct}%`;
        pBar.className = pct >= 100 ? 'bg-danger' : (pct >= 60 ? 'bg-success' : 'bg-primary');
      }
      document.getElementById('facLoadPctLabel').textContent = `${pct}% of weekly limit (${metrics.total_load_hours}/${metrics.weekly_lecture_limit} hrs)`;

      // Load my upcoming duties
      const mySchedules = await API.getSchedules();
      const listContainer = document.getElementById('facUpcomingDutiesList');
      if (listContainer) {
        if (!mySchedules.length) {
          listContainer.innerHTML = '<div style="color: #64748b; padding: 20px; text-align: center;">No scheduled lectures or duties assigned yet.</div>';
          return;
        }

        listContainer.innerHTML = mySchedules.slice(0, 6).map(s => `
          <div style="padding: 12px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 700; font-size: 13.5px; color: #1e3a8a;">${s.duty_title}</div>
              <div style="font-size: 12px; color: #64748b; margin-top: 3px;">
                📅 <strong>${s.day_of_week}, ${s.date}</strong> • ⏰ ${s.start_time} - ${s.end_time} • 📍 ${s.classroom_name || 'Designated Room'}
              </div>
              ${s.instructions ? `<div style="font-size: 11px; color: #b45309; margin-top: 2px;">⚠️ Note: ${s.instructions}</div>` : ''}
            </div>
            <span class="badge badge-regular">${s.schedule_type.replace('_', ' ').toUpperCase()}</span>
          </div>
        `).join('');
      }

    } catch (err) {
      console.error('Error loading faculty dashboard:', err);
    }
  }
};

window.Dashboard = Dashboard;
