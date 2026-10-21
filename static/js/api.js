/**
 * Faculty Load Management System - API Client
 */
const API = {
  BASE_URL: '',

  getToken() {
    return localStorage.getItem('flms_token');
  },

  setToken(token) {
    localStorage.setItem('flms_token', token);
  },

  removeToken() {
    localStorage.removeItem('flms_token');
    localStorage.removeItem('flms_user');
  },

  getCurrentUser() {
    try {
      const u = localStorage.getItem('flms_user');
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  setCurrentUser(user) {
    localStorage.setItem('flms_user', JSON.stringify(user));
  },

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const headers = options.headers || {};

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!headers['Content-Type'] && !(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        // Unauthorized
        this.removeToken();
        if (window.App && typeof window.App.showLogin === 'function') {
          window.App.showLogin();
        }
        throw new Error('Session expired. Please log in again.');
      }

      // Check if response is file download
      const contentType = response.headers.get('content-type');
      if (contentType && (contentType.includes('application/pdf') || contentType.includes('spreadsheetml'))) {
        if (!response.ok) throw new Error('File download failed');
        return await response.blob();
      }

      const data = await response.json();
      if (!response.ok) {
        const errorMsg = data.detail ? (typeof data.detail === 'string' ? data.detail : (data.detail.message || JSON.stringify(data.detail))) : 'An error occurred';
        const err = new Error(errorMsg);
        err.detail = data.detail;
        throw err;
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async login(username, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token);
    this.setCurrentUser(data.user);
    return data;
  },

  async getMe() {
    return await this.request('/api/auth/me');
  },

  async getDemoAccounts() {
    return await this.request('/api/auth/demo-accounts');
  },

  // Faculty Endpoints
  async getFaculty(params = {}) {
    const q = new URLSearchParams(params).toString();
    return await this.request(`/api/faculty/?${q}`);
  },

  async getFacultyById(id) {
    return await this.request(`/api/faculty/${id}`);
  },

  async getWorkloadSummary(params = {}) {
    const q = new URLSearchParams(params).toString();
    return await this.request(`/api/faculty/workload/summary?${q}`);
  },

  async createFaculty(payload) {
    return await this.request('/api/faculty/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateFaculty(id, payload) {
    return await this.request(`/api/faculty/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async deleteFaculty(id) {
    return await this.request(`/api/faculty/${id}`, {
      method: 'DELETE'
    });
  },

  // Schedule Endpoints
  async checkConflict(payload) {
    return await this.request('/api/schedules/check-conflict', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async getSchedules(params = {}) {
    const q = new URLSearchParams(params).toString();
    return await this.request(`/api/schedules/?${q}`);
  },

  async getWeeklyTimetable(params = {}) {
    const q = new URLSearchParams(params).toString();
    return await this.request(`/api/schedules/timetable?${q}`);
  },

  async createSchedule(payload, force = false) {
    return await this.request(`/api/schedules/?force=${force}`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async updateSchedule(id, payload, force = false) {
    return await this.request(`/api/schedules/${id}?force=${force}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async cancelSchedule(id) {
    return await this.request(`/api/schedules/${id}`, {
      method: 'DELETE'
    });
  },

  // Notification Endpoints
  async getNotifications(unreadOnly = false) {
    return await this.request(`/api/notifications/?unread_only=${unreadOnly}`);
  },

  async markNotificationRead(id) {
    return await this.request(`/api/notifications/${id}/read`, {
      method: 'PUT'
    });
  },

  async markAllNotificationsRead() {
    return await this.request('/api/notifications/mark-all-read', {
      method: 'POST'
    });
  },

  async getReminderPreferences() {
    return await this.request('/api/notifications/preferences');
  },

  async updateReminderPreferences(payload) {
    return await this.request('/api/notifications/preferences', {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
  },

  async triggerSchedulerNow() {
    return await this.request('/api/notifications/trigger-scheduler-now', {
      method: 'POST'
    });
  },

  async sendTestAlert() {
    return await this.request('/api/notifications/send-test-alert', {
      method: 'POST'
    });
  },

  // Master Data
  async getSubjects(department = '') {
    return await this.request(`/api/master/subjects?department=${department}`);
  },

  async getClasses(department = '') {
    return await this.request(`/api/master/classes?department=${department}`);
  },

  async getClassrooms() {
    return await this.request('/api/master/classrooms');
  },

  async getAuditLogs(limit = 50) {
    return await this.request(`/api/master/audit-logs?limit=${limit}`);
  },

  // Reports
  async getReportSummary(params = {}) {
    const q = new URLSearchParams(params).toString();
    return await this.request(`/api/reports/summary?${q}`);
  },

  getExcelReportUrl(department = '', week = '') {
    return `/api/reports/export/excel?department=${department}&academic_week=${week}`;
  },

  getPdfReportUrl(department = '', week = '') {
    return `/api/reports/export/pdf?department=${department}&academic_week=${week}`;
  }
};

window.API = API;
