/**
 * Suryodaya College of Engineering & Technology (SCET)
 * Interactive Engine: Workload Simulator, Live Timetable Filter, and Navigation
 */

(function () {
  'use strict';

  // =========================================================================
  // 1. Workload Simulator State & Logic Engine
  // =========================================================================
  const initialSimState = {
    amit: { name: 'Dr. Amit Verma', hours: 18, limit: 16, status: 'Overloaded', badgeClass: 'scet-pill-overload' },
    priya: { name: 'Prof. Priya Patel', hours: 14, limit: 16, status: 'Balanced', badgeClass: 'scet-pill-balanced' },
    vikram: { name: 'Prof. Vikram Singh', hours: 8, limit: 16, status: 'Available', badgeClass: 'scet-pill-success' }
  };

  let currentSimState = JSON.parse(JSON.stringify(initialSimState));
  let dutyAssigned = false;

  function updateFacultyCardUI(id, data, isRecommended) {
    const hoursEl = document.getElementById(`simHours_${id}`);
    const barEl = document.getElementById(`simBar_${id}`);
    const badgeEl = document.getElementById(`simBadge_${id}`);
    const boxEl = document.getElementById(`simBox_${id}`);

    if (!hoursEl || !barEl || !badgeEl || !boxEl) return;

    const percentage = Math.min(Math.round((data.hours / data.limit) * 100), 125);
    hoursEl.textContent = `${data.hours} / ${data.limit} hrs (${percentage}%)`;

    barEl.style.width = `${Math.min(percentage, 100)}%`;
    if (data.hours > data.limit) {
      barEl.style.backgroundColor = '#EF4444';
      badgeEl.className = 'scet-status-pill scet-pill-overload';
      badgeEl.textContent = `Overloaded (${data.hours}h)`;
      hoursEl.style.color = '#EF4444';
    } else if (data.hours >= 14) {
      barEl.style.backgroundColor = '#2563EB';
      badgeEl.className = 'scet-status-pill scet-pill-balanced';
      badgeEl.textContent = `Balanced (${data.hours}h)`;
      hoursEl.style.color = '#2563EB';
    } else {
      barEl.style.backgroundColor = '#22A67A';
      badgeEl.className = 'scet-status-pill scet-pill-success';
      badgeEl.textContent = `Available (${data.hours}h)`;
      hoursEl.style.color = '#22A67A';
    }

    if (isRecommended) {
      boxEl.classList.add('recommended');
    } else {
      boxEl.classList.remove('recommended');
    }
  }

  function renderSimulator(feedbackMsg, icon = 'ℹ️', recId = null) {
    updateFacultyCardUI('amit', currentSimState.amit, recId === 'amit');
    updateFacultyCardUI('priya', currentSimState.priya, recId === 'priya');
    updateFacultyCardUI('vikram', currentSimState.vikram, recId === 'vikram');

    const feedbackIconEl = document.getElementById('simFeedbackIcon');
    const feedbackTextEl = document.getElementById('simFeedbackText');

    if (feedbackIconEl) feedbackIconEl.textContent = icon;
    if (feedbackTextEl) feedbackTextEl.innerHTML = feedbackMsg;
  }

  window.simulateDuty = function () {
    // 3-hour duty allocation simulation
    dutyAssigned = true;
    currentSimState.vikram.hours = 11;
    currentSimState.vikram.status = 'Balanced';

    renderSimulator(
      `<strong>New 3-Hour Duty Allocation: CS402 Systems Programming Lab</strong><br>
       • <strong>Dr. Amit Verma:</strong> Currently assigned 18 hrs (Already exceeding maximum 16h limit). Ineligible.<br>
       • <strong>Prof. Priya Patel:</strong> Currently assigned 14 hrs. Adding 3 hrs yields 17 hrs (>16h limit). Ineligible.<br>
       • <strong>Prof. Vikram Singh: Recommended!</strong> Currently 8 hrs + 3 hrs = 11 hrs (69% capacity, zero schedule collisions in Turing Lab 02).`,
      '💡',
      'vikram'
    );
  };

  window.runBalancer = function () {
    // Automated Load Rebalancing Algorithm execution
    currentSimState.amit.hours = 16;
    currentSimState.amit.status = 'Balanced';

    if (dutyAssigned) {
      currentSimState.vikram.hours = 13;
    } else {
      currentSimState.vikram.hours = 10;
    }
    currentSimState.vikram.status = 'Balanced';

    renderSimulator(
      `<strong>Workload Balancing Algorithm Executed Successfully!</strong><br>
       • <strong>Dr. Amit Verma:</strong> 2 overload hours transferred off schedule. Load reduced to 16 / 16 hrs (Standard Departmental Limit).<br>
       • <strong>Prof. Vikram Singh:</strong> Safely absorbed 2 lecture hours. Workload updated to ${currentSimState.vikram.hours} / 16 hrs (Balanced).<br>
       • <strong>Department Equilibrium:</strong> 100% faculty within approved limits. Conflict-free constraints preserved across all batches.`,
      '⚖️',
      null
    );
  };

  window.resetSimulator = function () {
    currentSimState = JSON.parse(JSON.stringify(initialSimState));
    dutyAssigned = false;
    renderSimulator(
      `Default departmental configuration loaded: Dr. Amit Verma is currently overloaded (18 / 16 hrs). Click <strong>"Simulate New 3-Hour Duty"</strong> or <strong>"Run Load Balancer"</strong> to inspect automated redistribution.`,
      'ℹ️',
      null
    );
  };

  // =========================================================================
  // 2. Interactive Timetable Dataset & Filtering
  // =========================================================================
  const sampleSchedule = [
    { id: 1, day: 'mon', type: 'lecture', profId: 'amit', subject: 'CS301 Data Structures & Algorithms', prof: 'Dr. Amit Verma', room: 'Aryabhata LH-301', time: '09:00 AM - 10:00 AM', batch: 'CSE-A (Sem 3)', dept: 'Computer Science' },
    { id: 2, day: 'mon', type: 'lab', profId: 'vikram', subject: 'CS402 Systems Programming Lab', prof: 'Prof. Vikram Singh', room: 'Turing Lab-2', time: '10:00 AM - 12:00 PM', batch: 'CSE-B (Sem 4)', dept: 'Computer Science' },
    { id: 3, day: 'mon', type: 'lecture', profId: 'priya', subject: 'CS601 Computer Networks', prof: 'Prof. Priya Patel', room: 'Aryabhata LH-302', time: '01:00 PM - 02:00 PM', batch: 'CSE-A (Sem 6)', dept: 'Computer Science' },
    { id: 4, day: 'tue', type: 'lecture', profId: 'amit', subject: 'CS503 Database Engineering', prof: 'Dr. Amit Verma', room: 'Aryabhata LH-301', time: '09:00 AM - 10:00 AM', batch: 'CSE-A (Sem 5)', dept: 'Computer Science' },
    { id: 5, day: 'tue', type: 'tutorial', profId: 'vikram', subject: 'CS301 Algorithm Problem Solving', prof: 'Prof. Vikram Singh', room: 'Aryabhata LH-303', time: '11:00 AM - 12:00 PM', batch: 'CSE-B (Sem 3)', dept: 'Computer Science' },
    { id: 6, day: 'tue', type: 'lecture', profId: 'priya', subject: 'CS401 Operating Systems & Architecture', prof: 'Prof. Priya Patel', room: 'Aryabhata LH-302', time: '02:00 PM - 03:00 PM', batch: 'CSE-A (Sem 4)', dept: 'Computer Science' },
    { id: 7, day: 'wed', type: 'lab', profId: 'amit', subject: 'CS503 Database & SQL Lab', prof: 'Dr. Amit Verma', room: 'Turing Lab-1', time: '09:00 AM - 11:00 AM', batch: 'CSE-A (Sem 5)', dept: 'Computer Science' },
    { id: 8, day: 'wed', type: 'lecture', profId: 'priya', subject: 'CS601 Socket Programming & Protocols', prof: 'Prof. Priya Patel', room: 'Aryabhata LH-301', time: '11:00 AM - 12:00 PM', batch: 'CSE-A (Sem 6)', dept: 'Computer Science' },
    { id: 9, day: 'thu', type: 'lecture', profId: 'vikram', subject: 'CS302 Computer Organization', prof: 'Prof. Vikram Singh', room: 'Aryabhata LH-302', time: '10:00 AM - 11:00 AM', batch: 'CSE-A (Sem 3)', dept: 'Computer Science' },
    { id: 10, day: 'thu', type: 'lab', profId: 'priya', subject: 'CS601 Network Security & Cryptography Lab', prof: 'Prof. Priya Patel', room: 'Turing Lab-3', time: '02:00 PM - 04:00 PM', batch: 'CSE-A (Sem 6)', dept: 'Computer Science' },
    { id: 11, day: 'fri', type: 'lecture', profId: 'amit', subject: 'CS701 Machine Learning Applications', prof: 'Dr. Amit Verma', room: 'Aryabhata LH-301', time: '09:00 AM - 10:00 AM', batch: 'CSE-A (Sem 7)', dept: 'Computer Science' },
    { id: 12, day: 'fri', type: 'tutorial', profId: 'vikram', subject: 'CS402 OS Kernel Case Study', prof: 'Prof. Vikram Singh', room: 'Aryabhata LH-303', time: '11:00 AM - 12:00 PM', batch: 'CSE-B (Sem 4)', dept: 'Computer Science' },
    { id: 13, day: 'sat', type: 'lecture', profId: 'amit', subject: 'CS801 Capstone Project Review & Evaluation', prof: 'Dr. Amit Verma', room: 'Seminar-Hall-A', time: '10:00 AM - 12:00 PM', batch: 'CSE Final Year', dept: 'Computer Science' },
    { id: 14, day: 'sat', type: 'lecture', profId: 'priya', subject: 'CS602 Cloud Virtualization & Distributed Systems', prof: 'Prof. Priya Patel', room: 'Aryabhata LH-302', time: '01:00 PM - 02:00 PM', batch: 'CSE-A (Sem 6)', dept: 'Computer Science' }
  ];

  let activeDayFilter = 'all';
  let activeTypeFilter = 'all';
  let activeFacultyFilter = 'all';

  function renderTimetable() {
    const gridEl = document.getElementById('scetTimetableGrid');
    if (!gridEl) return;

    const filtered = sampleSchedule.filter(item => {
      const dayMatch = activeDayFilter === 'all' || item.day === activeDayFilter;
      const typeMatch = activeTypeFilter === 'all' || item.type === activeTypeFilter;
      const facMatch = activeFacultyFilter === 'all' || item.profId === activeFacultyFilter;
      return dayMatch && typeMatch && facMatch;
    });

    if (filtered.length === 0) {
      gridEl.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 48px 20px; color: var(--color-text-muted);">
          <p style="font-size: 15px; font-weight: 600; color: var(--color-navy); margin-bottom: 6px;">No academic sessions found for this filter combination.</p>
          <p style="font-size: 13px; margin-bottom: 16px;">Try selecting "All Days" or clearing the session type filter.</p>
          <button class="scet-btn scet-btn-ghost" onclick="resetTimetableFilters()">Reset All Filters</button>
        </div>
      `;
      return;
    }

    gridEl.innerHTML = filtered.map(slot => {
      const typeClass = slot.type === 'lecture' ? 'lecture' : slot.type === 'lab' ? 'lab' : 'college';
      const typeLabel = slot.type.toUpperCase();
      return `
        <div class="scet-slot-card ${typeClass}" onclick="showSlotDetails(${slot.id})" title="Click to view detailed session parameters">
          <div class="scet-slot-time">
            <span>${slot.time}</span>
            <span style="font-weight: 700; opacity: 0.9;">${typeLabel}</span>
          </div>
          <div class="scet-slot-subj">${slot.subject}</div>
          <div class="scet-slot-prof">${slot.prof} • ${slot.batch}</div>
          <div class="scet-slot-bottom">
            <span class="scet-slot-room">📍 ${slot.room}</span>
            <span style="color: var(--color-success); font-weight: 700; font-size: 11px;">✓ No Conflict</span>
          </div>
        </div>
      `;
    }).join('');
  }

  window.filterTimetableDay = function (day, btn) {
    activeDayFilter = day;
    document.querySelectorAll('[data-day-filter]').forEach(el => el.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderTimetable();
  };

  window.filterTimetableType = function (type, btn) {
    activeTypeFilter = type;
    document.querySelectorAll('[data-type-filter]').forEach(el => el.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderTimetable();
  };

  window.filterTimetableFaculty = function (facId, btn) {
    activeFacultyFilter = facId;
    document.querySelectorAll('[data-faculty-filter]').forEach(el => el.classList.remove('active'));
    if (btn) btn.classList.add('active');
    renderTimetable();
  };

  window.resetTimetableFilters = function () {
    activeDayFilter = 'all';
    activeTypeFilter = 'all';
    activeFacultyFilter = 'all';
    document.querySelectorAll('[data-day-filter]').forEach(el => el.classList.toggle('active', el.dataset.dayFilter === 'all'));
    document.querySelectorAll('[data-type-filter]').forEach(el => el.classList.toggle('active', el.dataset.typeFilter === 'all'));
    document.querySelectorAll('[data-faculty-filter]').forEach(el => el.classList.toggle('active', el.dataset.facultyFilter === 'all'));
    renderTimetable();
  };

  window.showSlotDetails = function (slotId) {
    const slot = sampleSchedule.find(s => s.id === slotId);
    if (!slot) return;

    const modal = document.getElementById('scetSlotModal');
    const content = document.getElementById('scetSlotModalBody');
    if (modal && content) {
      content.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; border-bottom: 1px solid var(--color-border); padding-bottom: 12px;">
          <div>
            <span class="scet-tag" style="margin-bottom: 4px;">Verified Conflict-Free Session</span>
            <h3 style="font-family: var(--font-heading); font-size: 18px; font-weight: 800; color: var(--color-navy); margin: 0;">${slot.subject}</h3>
          </div>
          <span class="scet-status-pill scet-pill-success" style="font-size: 12px;">Zero Collisions</span>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; font-size: 13.5px; margin-bottom: 20px;">
          <div style="background: var(--color-bg); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--color-border);">
            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">Faculty Member</div>
            <div style="font-weight: 700; color: var(--color-navy); margin-top: 2px;">${slot.prof}</div>
          </div>
          <div style="background: var(--color-bg); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--color-border);">
            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">Time Slot</div>
            <div style="font-weight: 700; color: var(--color-navy); margin-top: 2px;">${slot.time}</div>
          </div>
          <div style="background: var(--color-bg); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--color-border);">
            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">Classroom / Lab</div>
            <div style="font-weight: 700; color: var(--color-navy); margin-top: 2px;">📍 ${slot.room}</div>
          </div>
          <div style="background: var(--color-bg); padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--color-border);">
            <div style="font-size: 11px; font-weight: 700; color: var(--color-text-muted); text-transform: uppercase;">Academic Batch</div>
            <div style="font-weight: 700; color: var(--color-navy); margin-top: 2px;">${slot.batch}</div>
          </div>
        </div>
        <div style="background: var(--color-orange-subtle); border: 1px solid var(--color-orange-border); padding: 12px 14px; border-radius: var(--radius-md); font-size: 12.5px; color: var(--color-text-primary); margin-bottom: 20px;">
          <strong>Algorithmic Validation:</strong> This schedule slot honors faculty weekly credit thresholds and prevents double-booking across shared department laboratories in Turing Center.
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button type="button" class="scet-btn scet-btn-ghost" onclick="closeSlotModal()">Close Details</button>
          <button type="button" class="scet-btn scet-btn-primary" onclick="closeSlotModal(); openLoginModal();">HOD Timetable Editor ↗</button>
        </div>
      `;
      modal.classList.add('open');
    }
  };

  window.closeSlotModal = function () {
    const modal = document.getElementById('scetSlotModal');
    if (modal) modal.classList.remove('open');
  };

  // =========================================================================
  // 3. Login Modal Handling & Password Toggle
  // =========================================================================
  window.openLoginModal = function () {
    const modal = document.getElementById('scetLoginModal');
    if (modal) {
      modal.classList.add('open');
      const userField = document.getElementById('loginUsername');
      if (userField) {
        setTimeout(() => userField.focus(), 100);
      }
    }
  };

  window.closeLoginModal = function () {
    const modal = document.getElementById('scetLoginModal');
    if (modal) {
      modal.classList.remove('open');
    }
  };

  window.togglePasswordVisibility = function () {
    const passField = document.getElementById('loginPassword');
    const toggleIcon = document.getElementById('scetPwToggleIcon');
    if (!passField) return;

    if (passField.type === 'password') {
      passField.type = 'text';
      if (toggleIcon) toggleIcon.textContent = '🔒';
    } else {
      passField.type = 'password';
      if (toggleIcon) toggleIcon.textContent = '👁️';
    }
  };

  // =========================================================================
  // 4. Navigation, Sticky Header & Scroll Spy
  // =========================================================================
  function initNavigation() {
    const navbar = document.querySelector('.scet-navbar');
    const hamburger = document.getElementById('scetHamburgerBtn');
    const mobileMenu = document.getElementById('scetMobileMenu');

    // Sticky header shadow on scroll
    window.addEventListener('scroll', () => {
      if (window.scrollY > 20) {
        navbar?.classList.add('scrolled');
      } else {
        navbar?.classList.remove('scrolled');
      }
      updateScrollSpy();
    }, { passive: true });

    // Mobile menu toggle
    if (hamburger && mobileMenu) {
      hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
        mobileMenu.classList.toggle('open');
      });

      // Close menu on link click
      mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
          mobileMenu.classList.remove('open');
        });
      });
    }

    // Modal dismiss on backdrop click or Escape key
    const modalOverlay = document.getElementById('scetLoginModal');
    if (modalOverlay) {
      modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) closeLoginModal();
      });
    }

    const slotModalOverlay = document.getElementById('scetSlotModal');
    if (slotModalOverlay) {
      slotModalOverlay.addEventListener('click', (e) => {
        if (e.target === slotModalOverlay) closeSlotModal();
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeLoginModal();
        closeSlotModal();
      }
    });
  }

  // Active section scroll spy
  function updateScrollSpy() {
    const sections = ['hero', 'platform', 'workflow', 'simulator', 'timetable', 'identity'];
    const scrollPos = window.scrollY + 120;

    for (let i = sections.length - 1; i >= 0; i--) {
      const sectionEl = document.getElementById(sections[i]);
      if (sectionEl && sectionEl.offsetTop <= scrollPos) {
        document.querySelectorAll('.scet-nav-menu .scet-nav-link').forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${sections[i]}`);
        });
        break;
      }
    }
  }

  // =========================================================================
  // 5. Initialize on DOM Ready
  // =========================================================================
  document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    renderTimetable();
  });

})();
