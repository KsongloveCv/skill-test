(function (W) {
  if (W.GameEngine) return;

const {
  ROLES, ROLE_META, PHASES, ROLE_DISTRIBUTION,
  AI_NAMES, isWolf, isGood,
} = W.WerewolfConsts;

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function breakTie(ids) {
  return pickRandom(ids);
}

class GameEngine {
  constructor() {
    this.listeners = new Set();
    this.sessionId = 0;
    this.fastMode = localStorage.getItem('werewolf-fast') === '1';
    this.reset();
  }

  setFastMode(on) {
    this.fastMode = on;
    localStorage.setItem('werewolf-fast', on ? '1' : '0');
    this.emit();
  }

  reset() {
    this.sessionId += 1;
    this.humanName = '';
    this.playerCount = 6;
    this.players = [];
    this.round = 1;
    this.phase = null;
    this.isNight = true;
    this.log = [];
    this.pendingHunter = null;
    this.witchSaveUsed = false;
    this.witchPoisonUsed = false;
    this.nightKillTarget = null;
    this.nightPoisonTarget = null;
    this.witchSavedTonight = false;
    this.wolfVotes = {};
    this.dayVotes = {};
    this.seerChecks = {};
    this.humanSeerHistory = [];
    this.lastVoteResult = null;
    this.winner = null;
    this.aiMemory = {};
    this.discussionLines = [];
    this.waitingForHuman = false;
    this.humanActionResolver = null;
    this.lastNightDeaths = [];
    this.witchDraft = { save: false, poisonId: null };
  }

  onChange(fn) {
    this.listeners.add(fn);
    return () => this.listeners.delete(fn);
  }

  emit() {
    this.listeners.forEach((fn) => fn(this.getSnapshot()));
  }

  getSnapshot() {
    const human = this.getHuman();
    return {
      humanName: this.humanName,
      playerCount: this.playerCount,
      players: this.players.map((p) => ({ ...p })),
      round: this.round,
      phase: this.phase,
      isNight: this.isNight,
      log: this.getVisibleLog(human),
      pendingHunter: this.pendingHunter,
      witchSaveUsed: this.witchSaveUsed,
      witchPoisonUsed: this.witchPoisonUsed,
      nightKillTarget: this.nightKillTarget,
      witchDraft: { ...this.witchDraft },
      winner: this.winner,
      discussionLines: [...this.discussionLines],
      waitingForHuman: this.waitingForHuman,
      humanPlayer: human ? { ...human } : null,
      alivePlayers: this.getAlive().map((p) => ({ ...p })),
      wolves: this.getWolves().map((p) => ({ ...p })),
      humanSeerHistory: [...this.humanSeerHistory],
      lastVoteResult: this.lastVoteResult ? { ...this.lastVoteResult } : null,
      fastMode: this.fastMode,
      wolfTeammates: this.getWolfTeammates().map((p) => ({ ...p })),
    };
  }

  getVisibleLog(human) {
    return this.log.filter((entry) => this.canSeeLog(entry, human)).map((e) => ({ ...e }));
  }

  canSeeLog(entry, human) {
    if (!entry.audience || entry.audience === 'all') return true;
    if (entry.audience === 'dead' && human?.alive) return false;
    if (entry.audience === 'wolf' && human && isWolf(human.role)) return true;
    if (entry.audience === 'seer' && human?.role === ROLES.SEER) return true;
    if (entry.audience === 'witch' && human?.role === ROLES.WITCH) return true;
    if (entry.audience === 'self' && human && entry.playerId === human.id) return true;
    return false;
  }

  getHuman() {
    return this.players.find((p) => p.isHuman) ?? null;
  }

  getAlive() {
    return this.players.filter((p) => p.alive);
  }

  getWolves() {
    return this.players.filter((p) => p.alive && isWolf(p.role));
  }

  getGoodAlive() {
    return this.players.filter((p) => p.alive && isGood(p.role));
  }

  addLog(text, type = 'info', options = {}) {
    this.log.unshift({
      text,
      type,
      round: this.round,
      isNight: this.isNight,
      audience: options.audience ?? 'all',
      playerId: options.playerId ?? null,
    });
    if (this.log.length > 100) this.log.pop();
  }

  addSuspicion(observerId, targetId, delta, reason) {
    if (observerId == null || targetId == null) return;
    const mem = this.aiMemory[observerId];
    if (!mem) return;
    mem.suspicion[targetId] = (mem.suspicion[targetId] ?? 0) + delta;
    if (reason) {
      mem.reasons = mem.reasons ?? {};
      mem.reasons[targetId] = reason;
    }
  }

  spreadSuspicion(fromId, delta) {
    const alive = this.getAlive().filter((p) => p.id !== fromId);
    alive.forEach((p) => {
      Object.keys(this.aiMemory).forEach((oid) => {
        if (Number(oid) !== fromId) {
          this.addSuspicion(Number(oid), p.id, delta * (Math.random() * 0.5 + 0.5));
        }
      });
    });
  }

  start(humanName, playerCount) {
    this.reset();
    const sessionId = this.sessionId;

    this.humanName = humanName.trim() || '玩家';
    this.playerCount = playerCount;

    const roles = shuffle(ROLE_DISTRIBUTION[playerCount]);
    const names = shuffle(AI_NAMES.filter((n) => n !== this.humanName)).slice(0, playerCount - 1);
    const humanIndex = Math.floor(Math.random() * playerCount);

    this.players = roles.map((role, i) => {
      const isHuman = i === humanIndex;
      return {
        id: i,
        name: isHuman ? this.humanName : names[i - (i > humanIndex ? 1 : 0)] ?? `玩家${i + 1}`,
        isHuman,
        role,
        alive: true,
        votedOut: false,
        deathReason: null,
      };
    });

    this.players.forEach((p) => {
      this.aiMemory[p.id] = { suspicion: {}, reasons: {}, knownRole: null };
    });

    this.addLog(`对局开始，共 ${playerCount} 名玩家入座。`, 'system');
    this.emit();
    this.beginNight(sessionId);
  }

  isActive(sessionId) {
    return sessionId === this.sessionId;
  }

  async beginNight(sessionId) {
    if (!this.isActive(sessionId)) return;
    this.isNight = true;
    this.nightKillTarget = null;
    this.nightPoisonTarget = null;
    this.witchSavedTonight = false;
    this.wolfVotes = {};
    this.lastVoteResult = null;
    this.addLog(`—— 第 ${this.round} 夜 ——`, 'phase');
    await this.runPhase(PHASES.NIGHT_WOLF, sessionId);
  }

  async beginDay(sessionId) {
    if (!this.isActive(sessionId)) return;
    this.isNight = false;
    this.dayVotes = {};
    this.discussionLines = [];
    this.addLog(`—— 第 ${this.round} 日 ——`, 'phase');
    await this.runPhase(PHASES.DAY_ANNOUNCE, sessionId);
  }

  async runPhase(phase, sessionId) {
    if (!this.isActive(sessionId) || this.winner) return;
    this.phase = phase;
    this.waitingForHuman = false;
    this.emit();

    switch (phase) {
      case PHASES.NIGHT_WOLF:
        await this.phaseNightWolf(sessionId);
        break;
      case PHASES.NIGHT_SEER:
        await this.phaseNightSeer(sessionId);
        break;
      case PHASES.NIGHT_WITCH:
        await this.phaseNightWitch(sessionId);
        break;
      case PHASES.NIGHT_RESOLVE:
        await this.phaseNightResolve(sessionId);
        break;
      case PHASES.DAY_ANNOUNCE:
        await this.phaseDayAnnounce(sessionId);
        break;
      case PHASES.DAY_HUNTER:
        await this.phaseDayHunter(sessionId);
        break;
      case PHASES.DAY_DISCUSS:
        await this.phaseDayDiscuss(sessionId);
        break;
      case PHASES.DAY_VOTE:
        await this.phaseDayVote(sessionId);
        break;
      default:
        break;
    }
  }

  delay(ms) {
    const actual = this.fastMode ? Math.min(ms, 60) : ms;
    return new Promise((r) => setTimeout(r, actual));
  }

  waitForHumanAction() {
    this.waitingForHuman = true;
    this.emit();
    return new Promise((resolve) => {
      this.humanActionResolver = resolve;
    });
  }

  resolveHumanAction(payload) {
    if (!this.humanActionResolver) return;

    if (this.phase === PHASES.NIGHT_WITCH && payload?.draft) {
      this.witchDraft = {
        save: payload.save ?? this.witchDraft.save,
        poisonId: payload.poisonId !== undefined ? payload.poisonId : this.witchDraft.poisonId,
      };
      this.emit();
      if (!payload.confirm) return;
      payload = { save: this.witchDraft.save, poisonId: this.witchDraft.poisonId };
      this.witchDraft = { save: false, poisonId: null };
    }

    const r = this.humanActionResolver;
    this.humanActionResolver = null;
    this.waitingForHuman = false;
    r(payload);
    this.emit();
  }

  getSelectableTargetIds() {
    const human = this.getHuman();
    if (!human?.alive || !this.waitingForHuman) return [];

    const alive = this.getAlive();
    const others = alive.filter((p) => p.id !== human.id);

    switch (this.phase) {
      case PHASES.NIGHT_WOLF:
        return isWolf(human.role) ? alive.filter((p) => !isWolf(p.role)).map((p) => p.id) : [];
      case PHASES.NIGHT_SEER:
        return human.role === ROLES.SEER ? others.map((p) => p.id) : [];
      case PHASES.NIGHT_WITCH:
        return human.role === ROLES.WITCH && !this.witchPoisonUsed
          ? others.map((p) => p.id) : [];
      case PHASES.DAY_HUNTER:
        return this.pendingHunter?.id === human.id ? others.map((p) => p.id) : [];
      case PHASES.DAY_VOTE:
        return others.map((p) => p.id);
      default:
        return [];
    }
  }

  async phaseNightWolf(sessionId) {
    const wolves = this.getWolves();
    const targets = this.getAlive().filter((p) => !isWolf(p.role));

    for (const wolf of wolves) {
      if (!this.isActive(sessionId)) return;
      if (wolf.isHuman) {
        const choice = await this.waitForHumanAction();
        if (!this.isActive(sessionId)) return;
        this.wolfVotes[wolf.id] = choice?.targetId ?? pickRandom(targets)?.id;
      } else {
        await this.delay(400);
        this.wolfVotes[wolf.id] = this.aiPickWolfTarget(wolf);
      }
    }

    const tally = {};
    Object.values(this.wolfVotes).forEach((id) => {
      tally[id] = (tally[id] ?? 0) + 1;
    });
    const max = Math.max(...Object.values(tally), 0);
    const tied = Object.entries(tally).filter(([, v]) => v === max).map(([id]) => Number(id));
    this.nightKillTarget = tied.length ? breakTie(tied) : null;

    const human = this.getHuman();
    if (isWolf(human?.role)) {
      const target = this.players.find((p) => p.id === this.nightKillTarget);
      this.addLog(
        target ? `狼人阵营选定刀口：${target.name}` : '狼人阵营未达成一致。',
        'night',
        { audience: 'wolf' },
      );
    }
    await this.runPhase(PHASES.NIGHT_SEER, sessionId);
  }

  aiPickWolfTarget(wolf) {
    const targets = this.getAlive().filter((p) => p.id !== wolf.id && !isWolf(p.role));
    const priority = targets.filter((t) =>
      [ROLES.SEER, ROLES.WITCH, ROLES.HUNTER].includes(t.role));
    const pool = priority.length ? priority : targets;
    const mem = this.aiMemory[wolf.id]?.suspicion ?? {};
    const weighted = pool.map((t) => ({
      p: t,
      w: (mem[t.id] ?? 0) + (priority.includes(t) ? 2 : 0) + Math.random(),
    }));
    weighted.sort((a, b) => b.w - a.w);
    return weighted[0]?.p.id ?? targets[0]?.id;
  }

  async phaseNightSeer(sessionId) {
    const seer = this.players.find((p) => p.alive && p.role === ROLES.SEER);
    if (!seer) {
      await this.runPhase(PHASES.NIGHT_WITCH, sessionId);
      return;
    }

    let targetId;
    if (seer.isHuman) {
      const choice = await this.waitForHumanAction();
      if (!this.isActive(sessionId)) return;
      targetId = choice?.targetId;
    } else {
      await this.delay(500);
      targetId = this.aiPickSeerTarget(seer);
    }

    const target = this.players.find((p) => p.id === targetId);
    if (target) {
      const result = isWolf(target.role) ? '狼人' : '好人';
      this.seerChecks[seer.id] = { targetId, result, round: this.round };
      if (seer.isHuman) {
        this.humanSeerHistory.unshift({ targetId, targetName: target.name, result, round: this.round });
        this.addLog(`你查验了 ${target.name}：${result}`, 'seer', { audience: 'self', playerId: seer.id });
        if (isWolf(target.role)) {
          this.addSuspicion(seer.id, targetId, 3, '查验为狼');
        }
      } else {
        this.addLog(`${seer.name} 完成了查验。`, 'night');
        this.aiMemory[seer.id].knownRole = { id: targetId, isWolf: isWolf(target.role) };
        if (isWolf(target.role)) {
          this.addSuspicion(seer.id, targetId, 3, '查验为狼');
        }
      }
    }
    await this.runPhase(PHASES.NIGHT_WITCH, sessionId);
  }

  aiPickSeerTarget(seer) {
    const checked = new Set(Object.values(this.seerChecks).map((c) => c.targetId));
    const pool = this.getAlive().filter((p) => p.id !== seer.id && !checked.has(p.id));
    return (pool.length ? pickRandom(pool) : pickRandom(this.getAlive().filter((p) => p.id !== seer.id)))?.id;
  }

  async phaseNightWitch(sessionId) {
    const witch = this.players.find((p) => p.alive && p.role === ROLES.WITCH);
    if (!witch) {
      await this.runPhase(PHASES.NIGHT_RESOLVE, sessionId);
      return;
    }

    const killTarget = this.players.find((p) => p.id === this.nightKillTarget);
    let save = false;
    let poisonId = null;

    if (witch.isHuman) {
      this.witchDraft = { save: false, poisonId: null };
      const choice = await this.waitForHumanAction();
      if (!this.isActive(sessionId)) return;
      save = choice?.save ?? false;
      poisonId = choice?.poisonId ?? null;
    } else {
      await this.delay(600);
      const aiChoice = this.aiWitchChoice(witch, killTarget);
      save = aiChoice.save;
      poisonId = aiChoice.poisonId;
    }

    if (save && !this.witchSaveUsed && killTarget?.alive) {
      this.witchSaveUsed = true;
      this.witchSavedTonight = true;
      this.addLog(`你使用解药救活了 ${killTarget.name}。`, 'witch', { audience: 'witch', playerId: witch.id });
    }
    if (poisonId != null && !this.witchPoisonUsed) {
      const poisonTarget = this.players.find((p) => p.id === poisonId && p.alive);
      if (poisonTarget) {
        this.witchPoisonUsed = true;
        this.nightPoisonTarget = poisonId;
        this.addLog(`你使用毒药毒杀了 ${poisonTarget.name}。`, 'witch', { audience: 'witch', playerId: witch.id });
        this.spreadSuspicion(poisonTarget.id, 0.3);
      }
    }
    if (!save && poisonId == null && witch.isHuman) {
      this.addLog('你选择不使用药水。', 'witch', { audience: 'witch', playerId: witch.id });
    }
    await this.runPhase(PHASES.NIGHT_RESOLVE, sessionId);
  }

  aiWitchChoice(witch, killTarget) {
    let save = false;
    let poisonId = null;
    if (!this.witchSaveUsed && killTarget) {
      const saveRoles = [ROLES.SEER, ROLES.HUNTER, ROLES.WITCH];
      if (killTarget.id === witch.id || saveRoles.includes(killTarget.role)) {
        save = Math.random() > 0.2;
      }
    }
    if (!this.witchPoisonUsed && Math.random() > 0.45) {
      const suspects = this.getAlive().filter((p) => {
        if (p.id === witch.id) return false;
        if (save && p.id === killTarget?.id) return false;
        return true;
      });
      const mem = this.aiMemory[witch.id]?.suspicion ?? {};
      const ranked = suspects
        .map((p) => ({ p, s: mem[p.id] ?? 0 }))
        .sort((a, b) => b.s - a.s);
      const top = ranked.filter((r) => r.s > 0.5);
      poisonId = (top.length ? pickRandom(top).p : pickRandom(suspects))?.id ?? null;
    }
    return { save, poisonId };
  }

  async phaseNightResolve(sessionId) {
    const deaths = [];

    if (this.nightKillTarget != null && !this.witchSavedTonight) {
      const t = this.players.find((p) => p.id === this.nightKillTarget);
      if (t?.alive) deaths.push({ player: t, reason: 'wolf' });
    }
    if (this.nightPoisonTarget != null) {
      const t = this.players.find((p) => p.id === this.nightPoisonTarget);
      if (t?.alive && !deaths.find((d) => d.player.id === t.id)) {
        deaths.push({ player: t, reason: 'poison' });
      }
    }

    this.lastNightDeaths = deaths.map((d) => d.player.id);
    for (const { player, reason } of deaths) {
      this.killPlayer(player, reason, { silent: true });
    }

    if (this.checkWin()) return;
    await this.beginDay(sessionId);
  }

  killPlayer(player, reason, options = {}) {
    player.alive = false;
    player.deathReason = reason;
    if (!options.silent) {
      const reasonText = {
        wolf: '夜晚被狼人杀害',
        poison: '夜晚被女巫毒杀',
        vote: '白天被投票放逐',
        hunter: '被猎人开枪带走',
      }[reason] ?? '出局';
      this.addLog(`${player.name} ${reasonText}。`, 'death');
    }

    if (player.role === ROLES.HUNTER && reason !== 'poison') {
      this.pendingHunter = { ...player, canShoot: true };
    }

    this.spreadSuspicion(player.id, 0.2);
  }

  async phaseDayAnnounce(sessionId) {
    await this.delay(600);
    if (!this.isActive(sessionId)) return;

    if (this.lastNightDeaths.length === 0) {
      this.addLog('昨夜平安夜，无人出局。', 'info');
    } else {
      const names = this.lastNightDeaths
        .map((id) => this.players.find((p) => p.id === id)?.name)
        .filter(Boolean)
        .join('、');
      this.addLog(`天亮了，昨夜 ${names} 出局。`, 'info');
      this.lastNightDeaths.forEach((id) => {
        const p = this.players.find((pl) => pl.id === id);
        if (p) {
          this.addLog(`${p.name} 出局。`, 'death');
        }
      });
    }
    this.lastNightDeaths = [];
    this.emit();

    if (this.pendingHunter) {
      await this.runPhase(PHASES.DAY_HUNTER, sessionId);
      return;
    }
    await this.runPhase(PHASES.DAY_DISCUSS, sessionId);
  }

  async phaseDayHunter(sessionId) {
    const hunter = this.pendingHunter;
    if (!hunter?.canShoot) {
      this.pendingHunter = null;
      await this.runPhase(PHASES.DAY_DISCUSS, sessionId);
      return;
    }

    let targetId;
    if (hunter.isHuman) {
      const choice = await this.waitForHumanAction();
      if (!this.isActive(sessionId)) return;
      targetId = choice?.targetId;
    } else {
      await this.delay(500);
      const targets = this.getAlive();
      targetId = this.aiPickVoteTarget({ id: hunter.id }, targets);
    }

    if (targetId != null) {
      const target = this.players.find((p) => p.id === targetId);
      if (target?.alive) {
        this.killPlayer(target, 'hunter');
        this.addLog(`猎人 ${hunter.name} 开枪带走了 ${target.name}。`, 'hunter');
        if (isWolf(target.role)) {
          Object.keys(this.aiMemory).forEach((oid) => {
            this.addSuspicion(Number(oid), targetId, -1);
          });
        }
      }
    } else {
      this.addLog(`猎人 ${hunter.name} 选择不开枪。`, 'info');
    }
    this.pendingHunter = null;
    if (this.checkWin()) return;
    await this.runPhase(PHASES.DAY_DISCUSS, sessionId);
  }

  async phaseDayDiscuss(sessionId) {
    const human = this.getHuman();
    if (human?.alive) {
      const choice = await this.waitForHumanAction();
      if (!this.isActive(sessionId)) return;
      if (choice?.phrase) {
        const line = `${human.name}：${choice.phrase}`;
        this.discussionLines.push(line);
        this.addLog(line, 'chat');
        if (choice.suspectId != null) {
          this.spreadSuspicion(choice.suspectId, 0.4);
          Object.keys(this.aiMemory).forEach((oid) => {
            if (Number(oid) !== human.id) {
              this.addSuspicion(Number(oid), choice.suspectId, 0.3);
            }
          });
        }
      } else {
        this.addLog(`${human.name} 选择保持沉默。`, 'chat');
      }
    }

    this.generateDiscussion();
    await this.delay(this.fastMode ? 200 : 1200);
    if (!this.isActive(sessionId)) return;
    await this.runPhase(PHASES.DAY_VOTE, sessionId);
  }

  generateDiscussion() {
    const alive = this.getAlive();
    const lastDeath = this.players.filter((p) => !p.alive).slice(-1)[0];
    const templates = [
      (n) => `${n}：我觉得昨晚的信息很关键，大家说说看法。`,
      (n) => `${n}：有人跳预言家吗？`,
      (n) => `${n}：我先表水，我是好人。`,
      (n) => `${n}：注意发言逻辑，别被狼带节奏。`,
      (n) => lastDeath
        ? (name) => `${name}：${lastDeath.name} 出局很蹊跷，大家怎么想？`
        : (name) => `${name}：平安夜，狼人可能空刀或在憋大的。`,
    ];
    const speakers = shuffle(alive.filter((p) => !p.isHuman)).slice(0, Math.min(3, alive.length - 1));
    speakers.forEach((p) => {
      const line = pickRandom(templates)(p.name);
      this.discussionLines.push(line);
      this.addLog(line, 'chat');
      const others = alive.filter((x) => x.id !== p.id);
      if (others.length && Math.random() > 0.4) {
        const suspect = pickRandom(others);
        this.addSuspicion(p.id, suspect.id, 0.25);
      }
    });
    this.emit();
  }

  async phaseDayVote(sessionId) {
    const alive = this.getAlive();
    for (const p of alive) {
      if (!this.isActive(sessionId)) return;
      let targetId;
      if (p.isHuman) {
        const choice = await this.waitForHumanAction();
        if (!this.isActive(sessionId)) return;
        targetId = choice?.targetId;
      } else {
        await this.delay(350);
        targetId = this.aiPickVoteTarget(p, alive);
      }
      if (targetId != null) {
        this.dayVotes[p.id] = targetId;
      }
    }

    const tally = {};
    Object.entries(this.dayVotes).forEach(([voterId, targetId]) => {
      tally[targetId] = (tally[targetId] ?? 0) + 1;
      const voter = this.players.find((pl) => pl.id === Number(voterId));
      if (voter && !voter.isHuman) {
        this.addSuspicion(Number(voterId), targetId, 0.35);
      }
    });

    const voteDetails = Object.entries(tally)
      .map(([id, count]) => ({
        targetId: Number(id),
        targetName: this.players.find((p) => p.id === Number(id))?.name,
        count,
        voters: Object.entries(this.dayVotes)
          .filter(([, t]) => Number(t) === Number(id))
          .map(([v]) => this.players.find((p) => p.id === Number(v))?.name)
          .filter(Boolean),
      }))
      .sort((a, b) => b.count - a.count);

    this.lastVoteResult = { tally: voteDetails, round: this.round };

    if (voteDetails.length === 0) {
      this.addLog('今日无人被放逐。', 'info');
      await this.nextRound(sessionId);
      return;
    }

    const summary = voteDetails.map((v) => `${v.targetName} ${v.count} 票`).join('、');
    this.addLog(`投票结果：${summary}`, 'info');

    const topVotes = voteDetails[0].count;
    const tied = voteDetails.filter((v) => v.count === topVotes);

    if (tied.length > 1) {
      this.addLog('投票平票，今日无人出局。', 'info');
      await this.nextRound(sessionId);
      return;
    }

    const eliminated = this.players.find((p) => p.id === voteDetails[0].targetId);
    if (eliminated) {
      this.killPlayer(eliminated, 'vote');
      eliminated.votedOut = true;
      if (isWolf(eliminated.role)) {
        alive.forEach((p) => {
          if (!isWolf(this.players.find((pl) => pl.id === p.id)?.role)) {
            Object.keys(this.aiMemory).forEach((oid) => {
              voteDetails[0].voters.forEach((name) => {
                const voter = this.players.find((pl) => pl.name === name);
                if (voter) this.addSuspicion(Number(oid), voter.id, -0.2);
              });
            });
          }
        });
      } else {
        Object.keys(this.aiMemory).forEach((oid) => {
          voteDetails[0].voters.forEach((name) => {
            const voter = this.players.find((pl) => pl.name === name);
            if (voter) this.addSuspicion(Number(oid), voter.id, 0.4);
          });
        });
      }
    }

    if (this.checkWin()) return;

    if (this.pendingHunter) {
      await this.runPhase(PHASES.DAY_HUNTER, sessionId);
      return;
    }

    await this.nextRound(sessionId);
  }

  aiPickVoteTarget(voter, alive) {
    const voterPlayer = this.players.find((p) => p.id === voter.id);
    const others = alive.filter((p) => p.id !== voter.id);
    const mem = this.aiMemory[voter.id]?.suspicion ?? {};

    if (isWolf(voterPlayer?.role)) {
      const good = others.filter((p) => isGood(p.role));
      const weighted = good.map((p) => ({
        p,
        w: (mem[p.id] ?? 0) + ([ROLES.SEER, ROLES.WITCH].includes(p.role) ? 1.5 : 0) + Math.random(),
      }));
      weighted.sort((a, b) => b.w - a.w);
      return weighted[0]?.p.id ?? pickRandom(good)?.id;
    }

    const known = this.aiMemory[voter.id]?.knownRole;
    if (known?.isWolf && others.find((p) => p.id === known.id)) {
      return known.id;
    }

    const weighted = others.map((p) => ({
      p,
      w: (mem[p.id] ?? 0) + (isWolf(p.role) ? 2.5 : 0) + Math.random() * 0.3,
    }));
    weighted.sort((a, b) => b.w - a.w);
    return weighted[0]?.p.id ?? others[0]?.id;
  }

  async nextRound(sessionId) {
    if (!this.isActive(sessionId)) return;
    this.round += 1;
    if (this.checkWin()) return;
    await this.beginNight(sessionId);
  }

  checkWin() {
    const wolves = this.getWolves();
    const good = this.getGoodAlive();
    if (wolves.length === 0) {
      this.winner = 'good';
      this.phase = PHASES.GAME_OVER;
      this.addLog('所有狼人已被消灭，好人阵营胜利！', 'win');
      this.emit();
      return true;
    }
    if (wolves.length >= good.length) {
      this.winner = 'wolf';
      this.phase = PHASES.GAME_OVER;
      this.addLog('狼人数量已达到或超过好人，狼人阵营胜利！', 'win');
      this.emit();
      return true;
    }
    return false;
  }

  getWolfTeammates() {
    const human = this.getHuman();
    if (!human || !isWolf(human.role)) return [];
    return this.players.filter((p) => p.id !== human.id && isWolf(p.role));
  }
}

W.GameEngine = GameEngine;
W.WerewolfGame = { ROLES, ROLE_META, PHASES, isWolf, isGood };
})(window);
