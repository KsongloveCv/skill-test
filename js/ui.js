(function (W) {
  if (W.WerewolfUI) return;

const { ROLES, ROLE_META, PHASES, isWolf } = W.WerewolfConsts;

function getPhaseLabel(phase, round, isNight) {
  const labels = {
    [PHASES.NIGHT_WOLF]: `第 ${round} 夜 · 狼人行动`,
    [PHASES.NIGHT_SEER]: `第 ${round} 夜 · 预言家查验`,
    [PHASES.NIGHT_WITCH]: `第 ${round} 夜 · 女巫用药`,
    [PHASES.NIGHT_RESOLVE]: `第 ${round} 夜 · 天亮前`,
    [PHASES.DAY_ANNOUNCE]: `第 ${round} 日 · 公布死讯`,
    [PHASES.DAY_HUNTER]: `第 ${round} 日 · 猎人开枪`,
    [PHASES.DAY_DISCUSS]: `第 ${round} 日 · 自由讨论`,
    [PHASES.DAY_VOTE]: `第 ${round} 日 · 投票放逐`,
    [PHASES.GAME_OVER]: '对局结束',
  };
  return labels[phase] ?? (isNight ? `第 ${round} 夜` : `第 ${round} 日`);
}

const DISCUSS_PHRASES = [
  { phrase: '我是好人，先表水。', suspect: false },
  { phrase: '我怀疑刚才发言有问题的那位。', suspect: true },
  { phrase: '有人跳预言家吗？请报验人。', suspect: false },
  { phrase: '昨晚出局的信息很关键，大家分析一下。', suspect: false },
  { phrase: '我觉得票型有问题，注意跟票的人。', suspect: false },
];

function buildActionUI(snapshot, onAction) {
  const { phase, players, waitingForHuman, humanPlayer, nightKillTarget,
    witchSaveUsed, witchPoisonUsed, pendingHunter, witchDraft } = snapshot;

  if (!waitingForHuman) {
    const deadHint = humanPlayer && !humanPlayer.alive
      ? '<p class="action-placeholder">你已出局，正在观战…</p>'
      : '<p class="action-placeholder">等待其他玩家行动…</p>';
    return { html: deadHint, bind: null, selectableIds: [] };
  }

  if (!humanPlayer?.alive && phase !== PHASES.DAY_DISCUSS) {
    return { html: '<p class="action-placeholder">你已出局，正在观战…</p>', bind: null, selectableIds: [] };
  }

  const alive = players.filter((p) => p.alive);
  const others = alive.filter((p) => p.id !== humanPlayer.id);

  if (phase === PHASES.DAY_DISCUSS && humanPlayer.alive) {
    return buildDiscussUI(others, onAction);
  }

  if (phase === PHASES.NIGHT_WOLF && isWolf(humanPlayer.role)) {
    const targets = alive.filter((p) => !isWolf(p.role));
    return targetPicker('选择今晚要刀的目标（可点击牌桌）', targets, (id) => onAction({ targetId: id }));
  }

  if (phase === PHASES.NIGHT_SEER && humanPlayer.role === ROLES.SEER) {
    return targetPicker('选择要查验的玩家（可点击牌桌）', others, (id) => onAction({ targetId: id }));
  }

  if (phase === PHASES.NIGHT_WITCH && humanPlayer.role === ROLES.WITCH) {
    return buildWitchUI(snapshot, others, onAction);
  }

  if (phase === PHASES.DAY_HUNTER && pendingHunter?.id === humanPlayer.id) {
    return {
      html: `<p class="action-desc">你已出局，是否开枪？（可点击牌桌）</p>
        <div class="target-grid" id="hunter-grid"></div>
        <button type="button" class="btn-action skip" id="hunter-skip">不开枪</button>`,
      bind(root) {
        bindTargetGrid(root, '#hunter-grid', others, (id) => onAction({ targetId: id }));
        root.querySelector('#hunter-skip')?.addEventListener('click', () => onAction({ targetId: null }));
      },
      selectableIds: others.map((p) => p.id),
    };
  }

  if (phase === PHASES.DAY_VOTE) {
    return targetPicker('投票放逐一名玩家（可点击牌桌）', others, (id) => onAction({ targetId: id }));
  }

  return { html: '<p class="action-placeholder">等待中…</p>', bind: null, selectableIds: [] };
}

function buildDiscussUI(others, onAction) {
  let html = '<p class="action-desc">选择你的发言（可选怀疑对象）</p><div class="discuss-actions">';
  DISCUSS_PHRASES.forEach((item, i) => {
    html += `<button type="button" class="btn-action discuss-btn" data-idx="${i}">${item.phrase}</button>`;
  });
  html += '</div>';
  html += '<p class="action-sub">怀疑对象（可选）</p><div class="target-grid" id="suspect-grid"></div>';
  html += '<button type="button" class="btn-action skip" id="discuss-skip">保持沉默</button>';
  let selectedSuspect = null;

  return {
    html,
    bind(root) {
      bindTargetGrid(root, '#suspect-grid', others, (id) => {
        selectedSuspect = id;
        root.querySelectorAll('#suspect-grid .target-chip').forEach((btn) => {
          btn.classList.toggle('selected', Number(btn.dataset.id) === id);
        });
      }, true);
      root.querySelectorAll('.discuss-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
          const item = DISCUSS_PHRASES[Number(btn.dataset.idx)];
          onAction({
            phrase: item.phrase,
            suspectId: item.suspect ? selectedSuspect : null,
          });
        });
      });
      root.querySelector('#discuss-skip')?.addEventListener('click', () => onAction({ phrase: null }));
    },
    selectableIds: others.map((p) => p.id),
  };
}

function buildWitchUI(snapshot, others, onAction) {
  const { nightKillTarget, witchSaveUsed, witchPoisonUsed, players, witchDraft } = snapshot;
  const killTarget = players.find((p) => p.id === nightKillTarget);
  const killName = killTarget ? killTarget.name : '无人';
  const draft = witchDraft ?? { save: false, poisonId: null };

  let html = `<p class="action-desc">今晚狼刀目标：<strong>${killName}</strong></p><div class="witch-actions">`;

  if (!witchSaveUsed && killTarget?.alive) {
    const saved = draft.save ? ' active' : '';
    html += `<button type="button" class="btn-action save${saved}" data-action="toggle-save">解药：${draft.save ? '已选救' + killName : '不使用'}</button>`;
  }

  if (!witchPoisonUsed) {
    html += `<p class="action-sub">毒药目标（可选，可点击牌桌）</p><div class="target-grid" id="poison-grid"></div>`;
  }

  html += `<button type="button" class="btn-action confirm" data-action="confirm">确认本夜行动</button>`;
  html += `<button type="button" class="btn-action skip" data-action="skip-all">全部跳过</button></div>`;

  return {
    html,
    bind(root) {
      root.querySelector('[data-action="toggle-save"]')?.addEventListener('click', () => {
        onAction({ draft: true, save: !draft.save, confirm: false });
      });
      if (!witchPoisonUsed) {
        bindTargetGrid(root, '#poison-grid', others, (id) => {
          onAction({ draft: true, poisonId: id, confirm: false });
        }, true, draft.poisonId);
      }
      root.querySelector('[data-action="confirm"]')?.addEventListener('click', () => {
        onAction({ draft: true, confirm: true, save: draft.save, poisonId: draft.poisonId });
      });
      root.querySelector('[data-action="skip-all"]')?.addEventListener('click', () => {
        onAction({ save: false, poisonId: null });
      });
    },
    selectableIds: !witchPoisonUsed ? others.map((p) => p.id) : [],
  };
}

function bindTargetGrid(root, selector, targets, onPick, toggle = false, selectedId = null) {
  const grid = root.querySelector(selector);
  if (!grid) return;
  targets.forEach((p) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'target-chip';
    if (toggle && selectedId === p.id) btn.classList.add('selected');
    btn.dataset.id = p.id;
    btn.textContent = p.name;
    btn.addEventListener('click', () => onPick(p.id));
    grid.appendChild(btn);
  });
}

function targetPicker(title, targets, onPick) {
  return {
    html: `<p class="action-desc">${title}</p><div class="target-grid" id="pick-grid"></div>`,
    bind(root) {
      bindTargetGrid(root, '#pick-grid', targets, onPick);
    },
    selectableIds: targets.map((p) => p.id),
  };
}

function renderPlayerRing(container, snapshot, options = {}) {
  const { players, humanPlayer, wolfTeammates, phase } = snapshot;
  const { selectableIds = [], onSelectTarget, selectedTargetId } = options;
  const wolfMateIds = new Set(wolfTeammates?.map((p) => p.id) ?? []);
  const gameOver = phase === PHASES.GAME_OVER;

  if (container.dataset.count !== String(players.length)) {
    container.innerHTML = '';
    container.dataset.count = players.length;
  }

  players.forEach((p, i) => {
    const angle = (i / players.length) * 360 - 90;
    const rad = (angle * Math.PI) / 180;
    const rx = 42;
    const ry = 38;
    const x = 50 + rx * Math.cos(rad);
    const y = 50 + ry * Math.sin(rad);

    const meta = ROLE_META[p.role];
    let el = container.querySelector(`[data-player-id="${p.id}"]`);

    const isSelectable = selectableIds.includes(p.id);
    const isTeammate = !gameOver && wolfMateIds.has(p.id);
    const roleHint = gameOver || p.isHuman || !p.alive || isTeammate
      ? meta.icon
      : '?';

    const className = [
      'player-seat',
      !p.alive ? 'dead' : '',
      p.isHuman ? 'human' : '',
      isSelectable ? 'selectable' : '',
      isTeammate ? 'wolf-mate' : '',
      gameOver ? 'revealed' : '',
      selectedTargetId === p.id ? 'selected' : '',
    ].filter(Boolean).join(' ');

    const html = `
      <div class="seat-avatar" style="--role-color: ${meta.color}">${roleHint}</div>
      <span class="seat-name">${p.name}${p.isHuman ? ' · 你' : ''}${isTeammate ? ' · 狼队' : ''}</span>
      ${gameOver ? `<span class="seat-role">${meta.name}</span>` : ''}
      ${!p.alive && !gameOver ? '<span class="seat-dead">出局</span>' : ''}
      ${!p.alive && gameOver ? '<span class="seat-dead">出局</span>' : ''}
    `;

    if (!el) {
      el = document.createElement('div');
      el.dataset.playerId = p.id;
      container.appendChild(el);
    }

    el.className = className;
    el.style.left = `${x}%`;
    el.style.top = `${y}%`;
    el.innerHTML = html;

    if (isSelectable) {
      el.tabIndex = 0;
      el.setAttribute('role', 'button');
      el.setAttribute('aria-label', `选择 ${p.name}`);
      el.onclick = () => onSelectTarget?.(p.id);
      el.onkeydown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelectTarget?.(p.id);
        }
      };
    } else {
      el.removeAttribute('tabindex');
      el.removeAttribute('role');
      el.removeAttribute('aria-label');
      el.onclick = null;
      el.onkeydown = null;
    }
  });
}

function renderLog(container, log, prevLen = 0) {
  if (prevLen === 0 || log.length < prevLen) {
    container.innerHTML = log.slice(0, 30).map(formatLogEntry).join('');
    return log.length;
  }
  if (log.length > prevLen) {
    const newEntries = log.slice(0, log.length - prevLen);
    const frag = newEntries.map(formatLogEntry).join('');
    container.insertAdjacentHTML('afterbegin', frag);
    while (container.children.length > 30) {
      container.lastElementChild?.remove();
    }
  }
  return log.length;
}

function formatLogEntry(entry) {
  return `<li class="log-${entry.type}"><span class="log-round">${entry.isNight ? '夜' : '日'}${entry.round}</span>${entry.text}</li>`;
}

function renderSeerHistory(container, history) {
  if (!history?.length) {
    container.innerHTML = '<p class="panel-empty">暂无查验记录</p>';
    return;
  }
  container.innerHTML = history.map((h) =>
    `<li><span>第${h.round}夜</span><span>${h.targetName}</span><span class="seer-${h.result === '狼人' ? 'wolf' : 'good'}">${h.result}</span></li>`,
  ).join('');
}

function renderVoteResult(container, result) {
  if (!result?.tally?.length) {
    container.hidden = true;
    return;
  }
  container.hidden = false;
  container.innerHTML = result.tally.map((v) =>
    `<li><strong>${v.targetName}</strong> ${v.count} 票 <span class="vote-voters">(${v.voters.join('、')})</span></li>`,
  ).join('');
}

function showRoleDialog(dialog, humanPlayer) {
  if (!humanPlayer) return;
  const meta = ROLE_META[humanPlayer.role];
  document.getElementById('role-name').textContent = meta.name;
  document.getElementById('role-desc').textContent = meta.desc;
  const card = document.getElementById('role-card');
  card.style.setProperty('--role-accent', meta.color);
  dialog.showModal();
}

function showResultDialog(dialog, snapshot) {
  const { winner, players, humanPlayer, round } = snapshot;
  const humanCamp = humanPlayer ? ROLE_META[humanPlayer.role].camp : 'good';
  const won = (winner === 'wolf' && humanCamp === 'wolf') || (winner === 'good' && humanCamp === 'good');
  const humanMeta = humanPlayer ? ROLE_META[humanPlayer.role] : null;

  document.getElementById('result-label').textContent = won ? '恭喜你' : '很遗憾';
  document.getElementById('result-title').textContent = winner === 'wolf' ? '狼人阵营胜利' : '好人阵营胜利';
  document.getElementById('result-detail').textContent = won
    ? '你所在的阵营取得了最终胜利。'
    : '你所在的阵营未能坚持到最后。';

  const metaEl = document.getElementById('result-meta');
  if (metaEl && humanMeta) {
    metaEl.textContent = `你的身份：${humanMeta.name} · 共 ${round} 个回合`;
  }

  const reveal = document.getElementById('role-reveal');
  reveal.innerHTML = players.map((p) => {
    const m = ROLE_META[p.role];
    return `<li><span>${m.icon} ${p.name}</span><span>${m.name}</span></li>`;
  }).join('');

  if (!dialog.open) dialog.showModal();
}

function buildPostGameUI(handlers) {
  return {
    html: `
      <p class="action-desc">对局已结束。牌桌已公开全员身份，可在下方查看对局记录。</p>
      <div class="postgame-actions">
        <button type="button" class="btn-primary" data-action="again">再来一局</button>
        <button type="button" class="btn-secondary" data-action="lobby">返回大厅</button>
        <button type="button" class="btn-ghost" data-action="result">查看结算</button>
      </div>`,
    bind(root) {
      root.querySelector('[data-action="again"]')?.addEventListener('click', handlers.onPlayAgain);
      root.querySelector('[data-action="lobby"]')?.addEventListener('click', handlers.onBackLobby);
      root.querySelector('[data-action="result"]')?.addEventListener('click', handlers.onShowResult);
    },
  };
}

function updateCenterHint(el, snapshot) {
  const { phase, waitingForHuman, humanPlayer, discussionLines } = snapshot;
  if (phase === PHASES.GAME_OVER) {
    el.textContent = '对局已结束';
    return;
  }
  if (waitingForHuman && humanPlayer?.alive) {
    el.textContent = '轮到你行动';
    return;
  }
  if (humanPlayer && !humanPlayer.alive) {
    el.textContent = '观战模式';
    return;
  }
  if (phase === PHASES.DAY_DISCUSS && discussionLines.length) {
    el.textContent = discussionLines[discussionLines.length - 1];
    return;
  }
  el.textContent = getPhaseLabel(phase, snapshot.round, snapshot.isNight);
}

function handleTableSelect(snapshot, targetId, engine) {
  const { phase, humanPlayer, pendingHunter, witchDraft } = snapshot;
  if (!humanPlayer) return;

  if (phase === PHASES.NIGHT_WOLF && isWolf(humanPlayer.role)) {
    engine.resolveHumanAction({ targetId });
  } else if (phase === PHASES.NIGHT_SEER && humanPlayer.role === ROLES.SEER) {
    engine.resolveHumanAction({ targetId });
  } else if (phase === PHASES.NIGHT_WITCH && humanPlayer.role === ROLES.WITCH) {
    engine.resolveHumanAction({ draft: true, poisonId: targetId, save: witchDraft?.save ?? false, confirm: false });
  } else if (phase === PHASES.DAY_HUNTER && pendingHunter?.id === humanPlayer.id) {
    engine.resolveHumanAction({ targetId });
  } else if (phase === PHASES.DAY_VOTE) {
    engine.resolveHumanAction({ targetId });
  }
}

W.WerewolfUI = {
  getPhaseLabel,
  buildActionUI,
  buildPostGameUI,
  renderPlayerRing,
  renderLog,
  renderSeerHistory,
  renderVoteResult,
  showRoleDialog,
  showResultDialog,
  updateCenterHint,
  handleTableSelect,
};
})(window);
