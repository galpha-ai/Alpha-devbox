import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  _initTestDatabase,
  createTask,
  getAllTasks,
  getTaskById,
  setRegisteredAgent,
} from './db.js';
import { IpcDeps, processMessageIpc, processTaskIpc } from './ipc.js';
import { RegisteredAgent } from './types.js';

const MAIN_GROUP: RegisteredAgent = {
  name: 'Main',
  agentName: 'main',
  trigger: 'always',
  added_at: '2024-01-01T00:00:00.000Z',
};

const OTHER_GROUP: RegisteredAgent = {
  name: 'Other',
  agentName: 'other-group',
  trigger: '@Andy',
  added_at: '2024-01-01T00:00:00.000Z',
};

const THIRD_GROUP: RegisteredAgent = {
  name: 'Third',
  agentName: 'third-group',
  trigger: '@Andy',
  added_at: '2024-01-01T00:00:00.000Z',
};

let groups: Record<string, RegisteredAgent>;
let deps: IpcDeps;

beforeEach(() => {
  _initTestDatabase();

  groups = {
    'main@g.us': MAIN_GROUP,
    'other@g.us': OTHER_GROUP,
    'third@g.us': THIRD_GROUP,
  };

  setRegisteredAgent('main@g.us', MAIN_GROUP);
  setRegisteredAgent('other@g.us', OTHER_GROUP);
  setRegisteredAgent('third@g.us', THIRD_GROUP);

  deps = {
    sendMessage: async () => {},
    registeredAgents: () => groups,
  };
});

describe('message IPC authorization', () => {
  it('allows a session to send only to its own chat/thread scope', async () => {
    const sendMessage = vi.fn(async () => {});
    deps.sendMessage = sendMessage;

    await processMessageIpc(
      {
        type: 'message',
        chatJid: 'other@g.us',
        threadId: '1700000000.000100',
        text: 'hello',
      },
      {
        agentName: 'other-group',
        channelId: 'other@g.us',
        threadId: '1700000000.000100',
      },
      deps,
    );

    expect(sendMessage).toHaveBeenCalledWith('other@g.us', 'hello', {
      threadId: '1700000000.000100',
    });
  });

  it('blocks a session from sending into a different thread scope', async () => {
    const sendMessage = vi.fn(async () => {});
    deps.sendMessage = sendMessage;

    await processMessageIpc(
      {
        type: 'message',
        chatJid: 'other@g.us',
        threadId: null,
        text: 'hello',
      },
      {
        agentName: 'other-group',
        channelId: 'other@g.us',
        threadId: '1700000000.000100',
      },
      deps,
    );

    expect(sendMessage).not.toHaveBeenCalled();
  });
});

describe('schedule_task authorization', () => {
  it('allows an agent to schedule for itself', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'self task',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const allTasks = getAllTasks();
    expect(allTasks).toHaveLength(1);
    expect(allTasks[0].agentName).toBe('other-group');
  });

  it('blocks an agent from scheduling for another agent', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'unauthorized',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        targetJid: 'main@g.us',
      },
      'other-group',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });

  it('rejects schedule_task for an unregistered target JID', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'no target',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        targetJid: 'unknown@g.us',
      },
      'main',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });
});

describe('pause_task authorization', () => {
  beforeEach(() => {
    createTask({
      id: 'task-main',
      agentName: 'main',
      chat_jid: 'main@g.us',
      prompt: 'main task',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: '2025-06-01T00:00:00.000Z',
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });
    createTask({
      id: 'task-other',
      agentName: 'other-group',
      chat_jid: 'other@g.us',
      prompt: 'other task',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: '2025-06-01T00:00:00.000Z',
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });
  });

  it('allows an agent to pause its own task', async () => {
    await processTaskIpc(
      { type: 'pause_task', taskId: 'task-main' },
      'main',
      deps,
    );
    expect(getTaskById('task-main')!.status).toBe('paused');
  });

  it('allows another agent to pause its own task', async () => {
    await processTaskIpc(
      { type: 'pause_task', taskId: 'task-other' },
      'other-group',
      deps,
    );
    expect(getTaskById('task-other')!.status).toBe('paused');
  });

  it('blocks an agent from pausing another agents task', async () => {
    await processTaskIpc(
      { type: 'pause_task', taskId: 'task-main' },
      'other-group',
      deps,
    );
    expect(getTaskById('task-main')!.status).toBe('active');
  });
});

describe('resume_task authorization', () => {
  beforeEach(() => {
    createTask({
      id: 'task-paused',
      agentName: 'other-group',
      chat_jid: 'other@g.us',
      prompt: 'paused task',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: '2025-06-01T00:00:00.000Z',
      status: 'paused',
      created_at: '2024-01-01T00:00:00.000Z',
    });
  });

  it('blocks an agent from resuming another agents task', async () => {
    await processTaskIpc(
      { type: 'resume_task', taskId: 'task-paused' },
      'main',
      deps,
    );
    expect(getTaskById('task-paused')!.status).toBe('paused');
  });

  it('allows an agent to resume its own task', async () => {
    await processTaskIpc(
      { type: 'resume_task', taskId: 'task-paused' },
      'other-group',
      deps,
    );
    expect(getTaskById('task-paused')!.status).toBe('active');
  });

  it('blocks a third agent from resuming another agents task', async () => {
    await processTaskIpc(
      { type: 'resume_task', taskId: 'task-paused' },
      'third-group',
      deps,
    );
    expect(getTaskById('task-paused')!.status).toBe('paused');
  });
});

describe('cancel_task authorization', () => {
  it('allows an agent to cancel its own task', async () => {
    createTask({
      id: 'task-to-cancel',
      agentName: 'main',
      chat_jid: 'main@g.us',
      prompt: 'cancel me',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: null,
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    await processTaskIpc(
      { type: 'cancel_task', taskId: 'task-to-cancel' },
      'main',
      deps,
    );
    expect(getTaskById('task-to-cancel')).toBeUndefined();
  });

  it('allows another agent to cancel its own task', async () => {
    createTask({
      id: 'task-own',
      agentName: 'other-group',
      chat_jid: 'other@g.us',
      prompt: 'my task',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: null,
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    await processTaskIpc(
      { type: 'cancel_task', taskId: 'task-own' },
      'other-group',
      deps,
    );
    expect(getTaskById('task-own')).toBeUndefined();
  });

  it('blocks an agent from cancelling another agents task', async () => {
    createTask({
      id: 'task-foreign',
      agentName: 'main',
      chat_jid: 'main@g.us',
      prompt: 'not yours',
      schedule_type: 'once',
      schedule_value: '2025-06-01T00:00:00.000Z',
      context_mode: 'isolated',
      next_run: null,
      status: 'active',
      created_at: '2024-01-01T00:00:00.000Z',
    });

    await processTaskIpc(
      { type: 'cancel_task', taskId: 'task-foreign' },
      'other-group',
      deps,
    );
    expect(getTaskById('task-foreign')).toBeDefined();
  });
});

describe('IPC message authorization', () => {
  function isMessageAuthorized(
    sourceChatJid: string,
    sourceThreadId: string | null,
    targetChatJid: string,
    targetThreadId: string | null,
  ): boolean {
    return sourceChatJid === targetChatJid && sourceThreadId === targetThreadId;
  }

  it('allows matching chat and thread scope', () => {
    expect(
      isMessageAuthorized(
        'other@g.us',
        '1700000000.000100',
        'other@g.us',
        '1700000000.000100',
      ),
    ).toBe(true);
  });

  it('blocks a different chat even when thread matches', () => {
    expect(
      isMessageAuthorized(
        'other@g.us',
        '1700000000.000100',
        'main@g.us',
        '1700000000.000100',
      ),
    ).toBe(false);
  });

  it('blocks a different thread in the same chat', () => {
    expect(
      isMessageAuthorized(
        'other@g.us',
        '1700000000.000100',
        'other@g.us',
        '1700000000.000101',
      ),
    ).toBe(false);
  });
});

describe('schedule_task schedule types', () => {
  it('creates task with cron schedule and computes next_run', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'cron task',
        schedule_type: 'cron',
        schedule_value: '0 9 * * *',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks).toHaveLength(1);
    expect(tasks[0].schedule_type).toBe('cron');
    expect(tasks[0].next_run).toBeTruthy();
    expect(new Date(tasks[0].next_run!).getTime()).toBeGreaterThan(
      Date.now() - 60000,
    );
  });

  it('rejects invalid cron expression', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'bad cron',
        schedule_type: 'cron',
        schedule_value: 'not a cron',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });

  it('creates task with interval schedule', async () => {
    const before = Date.now();

    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'interval task',
        schedule_type: 'interval',
        schedule_value: '3600000',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks).toHaveLength(1);
    expect(tasks[0].schedule_type).toBe('interval');
    const nextRun = new Date(tasks[0].next_run!).getTime();
    expect(nextRun).toBeGreaterThanOrEqual(before + 3600000 - 1000);
    expect(nextRun).toBeLessThanOrEqual(Date.now() + 3600000 + 1000);
  });

  it('rejects invalid interval (non-numeric)', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'bad interval',
        schedule_type: 'interval',
        schedule_value: 'abc',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });

  it('rejects invalid interval (zero)', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'zero interval',
        schedule_type: 'interval',
        schedule_value: '0',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });

  it('rejects invalid once timestamp', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'bad once',
        schedule_type: 'once',
        schedule_value: 'not-a-date',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    expect(getAllTasks()).toHaveLength(0);
  });
});

describe('schedule_task context_mode', () => {
  it('accepts context_mode=group', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'group context',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        context_mode: 'group',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks[0].context_mode).toBe('group');
  });

  it('accepts context_mode=isolated', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'isolated context',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        context_mode: 'isolated',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks[0].context_mode).toBe('isolated');
  });

  it('defaults invalid context_mode to isolated', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'bad context',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        context_mode: 'bogus' as any,
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks[0].context_mode).toBe('isolated');
  });

  it('defaults missing context_mode to isolated', async () => {
    await processTaskIpc(
      {
        type: 'schedule_task',
        prompt: 'no context mode',
        schedule_type: 'once',
        schedule_value: '2025-06-01T00:00:00.000Z',
        targetJid: 'other@g.us',
      },
      'other-group',
      deps,
    );

    const tasks = getAllTasks();
    expect(tasks[0].context_mode).toBe('isolated');
  });
});
