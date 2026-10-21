/**
 * Notification & Automated Reminder System
 * In-app dropdown, sound/banner alert, and configurable reminder preferences
 */
const Notifications = {
  notificationsList: [],
  unreadCount: 0,

  async init() {
    console.log('[Notifications] Initializing Notification System...');
    this.bindEvents();
    await this.fetchBadgeCount();
  },

  bindEvents() {
    const bellBtn = document.getElementById('notifBellBtn');
    const dropdown = document.getElementById('notifDropdown');

    if (bellBtn && dropdown) {
      bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('show');
        if (dropdown.classList.contains('show')) {
          this.loadDropdownList();
        }
      });

      // Close on outside click
      document.addEventListener('click', (e) => {
        if (!bellBtn.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.classList.remove('show');
        }
      });
    }

    const markAllBtn = document.getElementById('notifMarkAllReadBtn');
    if (markAllBtn) {
      markAllBtn.addEventListener('click', () => this.markAllAsRead());
    }
  },

  async fetchBadgeCount() {
    try {
      const data = await API.getNotifications(false);
      this.unreadCount = data.unread_count;
      this.notificationsList = data.notifications;

      const badge = document.getElementById('notifBadge');
      if (badge) {
        if (this.unreadCount > 0) {
          badge.textContent = this.unreadCount > 9 ? '9+' : this.unreadCount;
          badge.style.display = 'inline-block';
        } else {
          badge.style.display = 'none';
        }
      }

      // Check for freshly arrived reminders to trigger browser notification
      const latestUnread = this.notificationsList.filter(n => !n.is_read && n.notification_type === 'reminder');
      if (latestUnread.length > 0) {
        const first = latestUnread[0];
        const lastNotifiedKey = `flms_notified_${first.id}`;
        if (!sessionStorage.getItem(lastNotifiedKey)) {
          sessionStorage.setItem(lastNotifiedKey, '1');
          App.sendBrowserNotification(first.title, first.message);
        }
      }
    } catch (err) {
      console.warn('Failed to fetch notifications badge:', err);
    }
  },

  async loadDropdownList() {
    const listEl = document.getElementById('notifDropdownList');
    if (!listEl) return;

    listEl.innerHTML = '<div style="padding: 16px; text-align: center; color: #64748b;">Loading notifications...</div>';

    try {
      const data = await API.getNotifications(false);
      this.notificationsList = data.notifications;
      this.unreadCount = data.unread_count;

      if (!this.notificationsList.length) {
        listEl.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b; font-size: 13px;">No notifications yet.</div>';
        return;
      }

      listEl.innerHTML = this.notificationsList.slice(0, 8).map(n => {
        const isReminder = n.notification_type === 'reminder';
        const icon = isReminder ? '⏰' : '📋';
        const timeAgo = this.formatTimeAgo(n.created_at);

        return `
          <div class="notif-item ${!n.is_read ? 'unread' : ''}" onclick="Notifications.handleNotificationClick(${n.id})">
            <div class="notif-icon-circle">${icon}</div>
            <div class="notif-content">
              <div class="notif-title">${n.title}</div>
              <div class="notif-msg">${n.message}</div>
              <div class="notif-time">${timeAgo} • via ${n.channel || 'in_app'}</div>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      listEl.innerHTML = '<div style="padding: 16px; color: #ef4444;">Failed to load notifications.</div>';
    }
  },

  async renderNotificationsPage() {
    const container = document.getElementById('notifPageList');
    if (!container) return;

    container.innerHTML = '<div style="padding: 24px; text-align: center;">Fetching all notifications...</div>';

    try {
      const data = await API.getNotifications(false);
      const list = data.notifications;

      if (!list.length) {
        container.innerHTML = '<div class="card" style="padding: 30px; text-align: center; color: #64748b;">You have no notifications or reminders.</div>';
        return;
      }

      container.innerHTML = list.map(n => {
        const isReminder = n.notification_type === 'reminder';
        const icon = isReminder ? '⏰' : '📌';
        const timeAgo = this.formatTimeAgo(n.created_at);

        return `
          <div class="card" style="margin-bottom: 12px; padding: 16px; border-left: 4px solid ${!n.is_read ? '#2563eb' : '#cbd5e1'};">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
              <div style="display: flex; gap: 12px; align-items: flex-start;">
                <div style="font-size: 20px;">${icon}</div>
                <div>
                  <h4 style="font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">${n.title}</h4>
                  <p style="font-size: 13px; color: #334155; white-space: pre-line; line-height: 1.4;">${n.message}</p>
                  <div style="font-size: 11px; color: #94a3b8; margin-top: 6px;">
                    Received: ${timeAgo} (${new Date(n.created_at).toLocaleString()}) • Channels: <strong>${n.channel}</strong>
                  </div>
                </div>
              </div>
              <div>
                ${!n.is_read ? `
                  <button class="btn btn-sm btn-outline-primary" onclick="Notifications.markSingleAsRead(${n.id})">Mark Read</button>
                ` : '<span class="badge badge-balanced">Read</span>'}
              </div>
            </div>
          </div>
        `;
      }).join('');
    } catch (err) {
      container.innerHTML = `<div class="conflict-banner conflict-danger">Error: ${err.message}</div>`;
    }
  },

  async handleNotificationClick(id) {
    await this.markSingleAsRead(id);
    document.getElementById('notifDropdown')?.classList.remove('show');
  },

  async markSingleAsRead(id) {
    try {
      await API.markNotificationRead(id);
      await this.fetchBadgeCount();
      if (App.activeView === 'view-notifications') {
        this.renderNotificationsPage();
      }
    } catch (err) {
      console.warn('Could not mark read:', err);
    }
  },

  async markAllAsRead() {
    try {
      await API.markAllNotificationsRead();
      App.toast('All notifications marked as read', 'success');
      await this.fetchBadgeCount();
      if (App.activeView === 'view-notifications') {
        this.renderNotificationsPage();
      }
      this.loadDropdownList();
    } catch (err) {
      App.toast('Failed to mark all as read', 'danger');
    }
  },

  async triggerAutomatedScheduler() {
    try {
      App.toast('Triggering automated schedule reminder engine...', 'info');
      await API.triggerSchedulerNow();
      await this.fetchBadgeCount();
      App.toast('Automated reminder check completed. Latest reminders refreshed.', 'success');
      if (App.activeView === 'view-notifications') {
        this.renderNotificationsPage();
      }
    } catch (err) {
      App.toast(`Scheduler execution error: ${err.message}`, 'danger');
    }
  },

  async sendTestAlert() {
    try {
      await API.sendTestAlert();
      App.toast('Live test reminder dispatched! Check notification bell and browser.', 'success');
      await this.fetchBadgeCount();
      this.loadDropdownList();
      App.sendBrowserNotification('⏰ Test Lecture Reminder', 'Reminder: You have an upcoming lecture in 15 minutes at LH-301.');
    } catch (err) {
      App.toast(`Error sending test alert: ${err.message}`, 'danger');
    }
  },

  formatTimeAgo(dateString) {
    if (!dateString) return '';
    const now = new Date();
    const past = new Date(dateString);
    const diffSeconds = Math.floor((now - past) / 1000);

    if (diffSeconds < 60) return 'Just now';
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }
};

window.Notifications = Notifications;
