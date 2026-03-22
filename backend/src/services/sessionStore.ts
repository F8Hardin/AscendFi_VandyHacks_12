export interface SessionRecord {
  sessionId: string;
  containerId: string;
  hostPort: number;
  status: 'starting' | 'ready' | 'dead';
  lastUsedAt: number;
  createdAt: number;
}

const sessions = new Map<string, SessionRecord>();

export const sessionStore = {
  get(sessionId: string): SessionRecord | undefined {
    return sessions.get(sessionId);
  },

  set(record: SessionRecord): void {
    sessions.set(record.sessionId, record);
  },

  touch(sessionId: string): void {
    const record = sessions.get(sessionId);
    if (record) {
      record.lastUsedAt = Date.now();
    }
  },

  delete(sessionId: string): void {
    sessions.delete(sessionId);
  },

  getAll(): SessionRecord[] {
    return Array.from(sessions.values());
  },

  updateStatus(sessionId: string, status: SessionRecord['status']): void {
    const record = sessions.get(sessionId);
    if (record) {
      record.status = status;
    }
  },
};
