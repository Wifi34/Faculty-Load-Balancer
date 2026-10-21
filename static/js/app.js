/**
 * Main Application Controller & Router
 * Role-Based Access: HOD vs Faculty
 */
const App = {
  currentUser: null,
  activeView: 'view-dashboard',
  pollingInterval: null,

  async init() {
    console.log('[App] Initializing Faculty Load Management System...');
    this.bindGlobalEvents();

    const token = API.getToken();
    const storedUser = API.getCurrentUser();

    if (token && storedUser) {
      try {
        const me = await API.getMe();
        this.currentUser = me;
        API.setCurrentUser(me);
        this.setupAuthenticatedUI();
      } catch (err) {
        console.warn('Stored token invalid, showing login screen');
        this.showLogin();
      }
    } else {
      this.showLogin();
    }
  },

  bindGlobalEvents() {
    // Mobile sidebar toggle
    const mobileBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.getElementById('sidebar');
    if (mobileBtn && sidebar) {
      mobileBtn.addEventListener('click', () => {
        sidebar.classList.toggle('mobile-open');
      });
    }

    // Nav Item Click delegation
    document.querySelectorAll('[data-view]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        const viewId = el.getAttribute('data-view');
        this.showView(viewId);
        if (sidebar) sidebar.classList.remove('mobile-open');
      });
    });

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => this.logout());
    }

    // Modal Close buttons
    document.querySelectorAll('.modal-close-trigger').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('show'));
      });
    });

    // Close modal on backdrop click
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('show');
        }
      });
    });
  },

  showLogin() {
    this.stopPolling();
    document.getElementById('appShell').style.display = 'none';
    document.getElementById('loginSection').style.display = 'flex';
    this.renderDemoAccountPills();
  },

  async renderDemoAccountPills() {
    const container = document.getElementById('demoPillsContainer');
    if (!container) return;

    try {
      const accounts = await API.getDemoAccounts();
      container.innerHTML = accounts.map(acc => `
        <button class="demo-pill-btn" onclick="App.fillDemoLogin('${acc.username}', '${acc.password}')" title="${acc.title} - ${acc.description}">
          <strong>${acc.role}</strong> (${acc.username})
        </button>
      `).join('');
    } catch (err) {
      container.innerHTML = `
        <button class="demo-pill-btn" onclick="App.fillDemoLogin('hod_cs', 'admin123')">HOD (hod_cs)</button>
        <button class="demo-pill-btn" onclick="App.fillDemoLogin('prof_amit', 'faculty123')">Faculty High Load (prof_amit)</button>
        <button class="demo-pill-btn" onclick="App.fillDemoLogin('prof_vikram', 'faculty123')">Faculty Available (prof_vikram)</button>
      `;
    }
  },

  fillDemoLogin(username, password) {
    const userField = document.getElementById('loginUsername');
    const passField = document.getElementById('loginPassword');
    if (userField && passField) {
      userField.value = username;
      passField.value = password;
      const form = document.getElementById('loginForm');
      if (form) form.requestSubmit();
    }
  },

  async handleLoginForm(e) {
    e.preventDefault();
    const userField = document.getElementById('loginUsername');
    const passField = document.getElementById('loginPassword');
    const errorBox = document.getElementById('loginErrorBox');
    const submitBtn = document.getElementById('loginSubmitBtn');

    if (!userField.value || !passField.value) return;

    submitBtn.disabled = true;
    submitBtn.textContent = 'Verifying credentials...';
    if (errorBox) errorBox.style.display = 'none';

    try {
      const resp = await API.login(userField.value.trim(), passField.value.trim());
      this.currentUser = resp.user;
      this.toast(`Welcome back, ${resp.user.full_name}!`, 'success');
      this.setupAuthenticatedUI();
    } catch (err) {
      if (errorBox) {
        errorBox.textContent = err.message || 'Login failed. Please check your credentials.';
        errorBox.style.display = 'block';
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Sign In to Portal';
    }
  },

  setupAuthenticatedUI() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('appShell').style.display = 'flex';

    // Populate user profile info in header and sidebar
    const user = this.currentUser;
    const isHod = user.role === 'hod';

    document.getElementById('headerUserName').textContent = user.full_name;
    document.getElementById('headerUserRole').textContent = isHod ? 'HOD (Administrator)' : 'Faculty Member';
    document.getElementById('sidebarUserName').textContent = user.full_name;
    document.getElementById('sidebarUserRole').textContent = isHod ? 'Head of Department' : (user.faculty_details ? user.faculty_details.designation : 'Faculty');
    document.getElementById('sidebarUserAvatar').textContent = user.full_name.charAt(0);

    // Toggle Role-based Navigation Elements
    document.querySelectorAll('.hod-only').forEach(el => {
      el.style.display = isHod ? '' : 'none';
    });
    document.querySelectorAll('.faculty-only').forEach(el => {
      el.style.display = !isHod ? '' : 'none';
    });

    // Request browser notification permission if not yet granted
    this.requestNotificationPermission();

    // Default landing view
    if (isHod) {
      this.showView('view-hod-dashboard');
    } else {
      this.showView('view-faculty-dashboard');
    }

    // Start background notification polling
    Notifications.init();
    this.startPolling();
  },

  showView(viewId) {
    this.activeView = viewId;

    // Update active nav styling
    document.querySelectorAll('.nav-item').forEach(item => {
      if (item.getAttribute('data-view') === viewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

    // Show selected view
    const target = document.getElementById(viewId);
    if (target) {
      target.classList.add('active');
      window.scrollTo(0, 0);

      // Trigger view-specific data refresh
      this.onViewActivated(viewId);
    }
  },

  onViewActivated(viewId) {
    if (viewId === 'view-hod-dashboard') {
      Dashboard.loadHodDashboard();
    } else if (viewId === 'view-faculty-dashboard') {
      Dashboard.loadFacultyDashboard();
    } else if (viewId === 'view-timetable') {
      Timetable.loadTimetable();
    } else if (viewId === 'view-workload-analytics') {
      Dashboard.loadWorkloadAnalytics();
    } else if (viewId === 'view-faculty-directory') {
      FacultyManager.loadFacultyDirectory();
    } else if (viewId === 'view-assign-duty') {
      Assignments.initAssignmentForm();
    } else if (viewId === 'view-reports') {
      this.loadReportsView();
    } else if (viewId === 'view-notifications') {
      Notifications.renderNotificationsPage();
    } else if (viewId === 'view-audit-logs') {
      this.loadAuditLogs();
    } else if (viewId === 'view-profile') {
      this.loadProfileView();
    }
  },

  startPolling() {
    this.stopPolling();
    // Poll notifications & reminders every 20 seconds
    this.pollingInterval = setInterval(() => {
      if (Notifications && typeof Notifications.fetchBadgeCount === 'function') {
        Notifications.fetchBadgeCount();
      }
    }, 20000);
  },

  stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  },

  async logout() {
    API.removeToken();
    this.currentUser = null;
    this.toast('You have been logged out safely.', 'info');
    this.showLogin();
  },

  requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('[Notification Permission]:', permission);
      });
    }
  },

  sendBrowserNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(title, {
        body: message,
        icon: '/static/assets/bell.png'
      });
    }
  },

  toast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">
        <span>${message}</span>
      </div>
      <button class="toast-close">&times;</button>
    `;

    toast.querySelector('.toast-close').addEventListener('click', () => {
      toast.remove();
    });

    container.appendChild(toast);
    setTimeout(() => {
      if (toast.parentNode) {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
      }
    }, 4000);
  },

  async loadReportsView() {
    const summaryBox = document.getElementById('reportMetricsSummary');
    if (!summaryBox) return;

    try {
      summaryBox.innerHTML = '<div style="padding: 20px; text-align: center;">Loading departmental reports...</div>';
      const data = await API.getReportSummary();

      summaryBox.innerHTML = `
        <div class="kpi-grid">
          <div class="kpi-card">
            <div class="kpi-icon kpi-blue">👥</div>
            <div class="kpi-body">
              <div class="kpi-label">Total Faculty</div>
              <div class="kpi-value">${data.total_faculty}</div>
              <div class="kpi-subtext">Active Teaching Staff</div>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-icon kpi-green">📚</div>
            <div class="kpi-body">
              <div class="kpi-label">Weekly Lectures</div>
              <div class="kpi-value">${data.total_lectures_scheduled}</div>
              <div class="kpi-subtext">Regular & Labs</div>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-icon kpi-amber">⏱️</div>
            <div class="kpi-body">
              <div class="kpi-label">Average Load</div>
              <div class="kpi-value">${data.average_teaching_load} hrs</div>
              <div class="kpi-subtext">Per faculty member</div>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-icon kpi-purple">⚖️</div>
            <div class="kpi-body">
              <div class="kpi-label">Workload Spread</div>
              <div class="kpi-value">${data.workload_breakdown.balanced} Balanced</div>
              <div class="kpi-subtext">${data.workload_breakdown.high} High | ${data.workload_breakdown.low} Low</div>
            </div>
          </div>
        </div>
      `;

      // Update download links
      const excelBtn = document.getElementById('downloadExcelBtn');
      const pdfBtn = document.getElementById('downloadPdfBtn');
      if (excelBtn) excelBtn.href = API.getExcelReportUrl();
      if (pdfBtn) pdfBtn.href = API.getPdfReportUrl();

    } catch (err) {
      summaryBox.innerHTML = `<div class="conflict-banner conflict-danger">Error loading report: ${err.message}</div>`;
    }
  },

  async loadAuditLogs() {
    const container = document.getElementById('auditLogsTableBody');
    if (!container) return;

    container.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">Fetching activity log...</td></tr>';
    try {
      const logs = await API.getAuditLogs(50);
      if (!logs.length) {
        container.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px;">No audit records found.</td></tr>';
        return;
      }
      container.innerHTML = logs.map(l => {
        const dt = new Date(l.timestamp).toLocaleString();
        return `
          <tr>
            <td><code>#${l.id}</code></td>
            <td><strong>${l.action}</strong></td>
            <td><span class="badge badge-low">${l.entity_type}</span></td>
            <td>${l.details || ''}</td>
            <td><small class="text-muted">${dt} (${l.username || 'System'})</small></td>
          </tr>
        `;
      }).join('');
    } catch (err) {
      container.innerHTML = `<tr><td colspan="5" class="text-danger">Failed to load logs: ${err.message}</td></tr>`;
    }
  },

  async loadProfileView() {
    const user = this.currentUser;
    document.getElementById('profileFullName').textContent = user.full_name;
    document.getElementById('profileUsername').textContent = user.username;
    document.getElementById('profileEmail').textContent = user.email;
    document.getElementById('profileRole').textContent = user.role.toUpperCase();

    if (user.faculty_details) {
      document.getElementById('profileDept').textContent = user.faculty_details.department;
      document.getElementById('profileDesignation').textContent = user.faculty_details.designation;
      document.getElementById('profileCode').textContent = user.faculty_details.faculty_code;
    }

    // Load reminder preferences into form
    try {
      const prefs = await API.getReminderPreferences();
      document.getElementById('prefLeadTime').value = prefs.lead_time_minutes;
      document.getElementById('prefBrowserToggle').checked = prefs.browser_enabled;
      document.getElementById('prefEmailToggle').checked = prefs.email_enabled;
    } catch (err) {
      console.warn('Could not fetch preferences:', err);
    }
  },

  async saveReminderPreferences(e) {
    e.preventDefault();
    const leadTime = parseInt(document.getElementById('prefLeadTime').value, 10);
    const browser = document.getElementById('prefBrowserToggle').checked;
    const email = document.getElementById('prefEmailToggle').checked;

    try {
      await API.updateReminderPreferences({
        lead_time_minutes: leadTime,
        browser_enabled: browser,
        email_enabled: email,
        notify_on_assignment: true
      });
      App.toast('Reminder preferences saved successfully!', 'success');
    } catch (err) {
      App.toast(`Failed to save preferences: ${err.message}`, 'danger');
    }
  }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
