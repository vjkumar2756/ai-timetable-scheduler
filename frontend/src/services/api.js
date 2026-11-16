const BASE_URL = '/api';

export const api = {
  // Settings & Health
  getHealth: () => fetch(`${BASE_URL}/health`).then(r => r.json()),
  getSettings: () => fetch(`${BASE_URL}/settings`).then(r => r.json()),
  
  // Entities
  getTeachers: () => fetch(`${BASE_URL}/teachers`).then(r => r.json()),
  createTeacher: (data) => fetch(`${BASE_URL}/teachers`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  updateTeacher: (id, data) => fetch(`${BASE_URL}/teachers/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),

  getClasses: () => fetch(`${BASE_URL}/classes`).then(r => r.json()),
  createClass: (data) => fetch(`${BASE_URL}/classes`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),
  updateClass: (id, data) => fetch(`${BASE_URL}/classes/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),

  getSubjects: () => fetch(`${BASE_URL}/subjects`).then(r => r.json()),
  createSubject: (data) => fetch(`${BASE_URL}/subjects`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),

  getRooms: () => fetch(`${BASE_URL}/rooms`).then(r => r.json()),
  createRoom: (data) => fetch(`${BASE_URL}/rooms`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).then(r => r.json()),

  // Scheduling
  generateSchedule: (algorithm = 'improved_backtracking', timeLimit = 20, seed = 42) => 
    fetch(`${BASE_URL}/schedule/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ algorithm, time_limit_seconds: timeLimit, random_seed: seed })
    }).then(r => r.json()),

  getSchedule: (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.class_id) params.append('class_id', filters.class_id);
    if (filters.teacher_id) params.append('teacher_id', filters.teacher_id);
    if (filters.room_id) params.append('room_id', filters.room_id);
    if (filters.day) params.append('day', filters.day);
    return fetch(`${BASE_URL}/schedule?${params.toString()}`).then(r => r.json());
  },

  validateManualEdit: (sessionId, targetDay, targetPeriod, targetRoomId, targetTeacherId) =>
    fetch(`${BASE_URL}/schedule/validate-edit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        target_day: targetDay,
        target_period: Number(targetPeriod),
        target_room_id: targetRoomId || null,
        target_teacher_id: targetTeacherId || null
      })
    }).then(r => r.json()),

  applyManualEdit: (sessionId, targetDay, targetPeriod, targetRoomId, targetTeacherId) =>
    fetch(`${BASE_URL}/schedule/sessions/${sessionId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        target_day: targetDay,
        target_period: Number(targetPeriod),
        target_room_id: targetRoomId || null,
        target_teacher_id: targetTeacherId || null
      })
    }).then(r => r.json()),

  // Operations
  cancelSession: (sessionId, reason) =>
    fetch(`${BASE_URL}/operations/cancel-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, reason })
    }).then(r => r.json()),

  closeClassDay: (classId, day, reason) =>
    fetch(`${BASE_URL}/operations/close-class-day`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ class_id: classId, day, reason })
    }).then(r => r.json()),

  findRescheduleSlots: (sessionId, altTeacherId) =>
    fetch(`${BASE_URL}/operations/reschedule/find-slots`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, alternative_teacher_id: altTeacherId || null })
    }).then(r => r.json()),

  applyReschedule: (payload) =>
    fetch(`${BASE_URL}/operations/reschedule/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r => r.json()),

  validateSwap: (s1Id, s2Id) =>
    fetch(`${BASE_URL}/operations/swap/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_1_id: s1Id, session_2_id: s2Id })
    }).then(r => r.json()),

  executeSwap: (s1Id, s2Id, requesterId, reason) =>
    fetch(`${BASE_URL}/operations/swap/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_1_id: s1Id, session_2_id: s2Id, requester_teacher_id: requesterId, reason })
    }).then(r => r.json()),

  getNotifications: () => fetch(`${BASE_URL}/operations/notifications`).then(r => r.json()),

  // Analytics & Benchmarks
  getWorkload: () => fetch(`${BASE_URL}/analytics/workload`).then(r => r.json()),
  getOverview: () => fetch(`${BASE_URL}/analytics/overview`).then(r => r.json()),
  getBenchmarks: () => fetch(`${BASE_URL}/analytics/benchmarks`).then(r => r.json()),

  // IO
  loadDataset: (name) => fetch(`${BASE_URL}/io/load-dataset/${name}`, { method: 'POST' }).then(r => r.json()),
  exportCsvUrl: () => `${BASE_URL}/io/export-csv`
};
