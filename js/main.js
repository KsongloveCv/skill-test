const { GameEngine } = window;
const { PHASES } = window.WerewolfConsts;

if (!GameEngine || !window.WerewolfUI) {
  console.error('月夜狼人杀：脚本未正确加载，请强制刷新页面或使用 start.sh 启动');
} else {
const {
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
} = window.WerewolfUI;

const engine = new GameEngine();

const screens = {
  lobby: document.getElementById('screen-lobby'),
  game: document.getElementById('screen-game'),
};

const els = {
  lobbyForm: document.getElementById('lobby-form'),
  playerName: document.getElementById('player-name'),
  phaseBadge: document.getElementById('phase-badge'),
  phaseIcon: document.getElementById('phase-icon'),
  phaseText: document.getElementById('phase-text'),
  roundLabel: document.getElementById('round-label'),
  playerRing: document.getElementById('player-ring'),
  centerHint: document.getElementById('center-hint'),
  actionPanel: document.getElementById('action-panel'),
  gameLog: document.getElementById('game-log'),
  seerHistory: document.getElementById('seer-history'),
  seerPanel: document.getElementById('seer-panel'),
  voteResult: document.getElementById('vote-result'),
  votePanel: document.getElementById('vote-panel'),
  roleDialog: document.getElementById('role-dialog'),
  resultDialog: document.getElementById('result-dialog'),
  btnRole: document.getElementById('btn-role'),
  btnRestart: document.getElementById('btn-restart'),
  btnPlayAgain: document.getElementById('btn-play-again'),
  btnBackLobby: document.getElementById('btn-back-lobby'),
  btnReviewTable: document.getElementById('btn-review-table'),
  btnFast: document.getElementById('btn-fast'),
  roleClose: document.getElementById('role-close'),
  wolfHint: document.getElementById('wolf-hint'),
};

const renderState = {
  logLen: 0,
  resultShown: false,
  resultDismissed: false,
  lastPhase: null,
  lastWaiting: false,
  lastSnapshot: null,
};

function showScreen(name) {
  Object.entries(screens).forEach(([key, el]) => {
    el.classList.toggle('active', key === name);
  });
}

function resetRenderState() {
  renderState.logLen = 0;
  renderState.resultShown = false;
  renderState.resultDismissed = false;
  renderState.lastPhase = null;
  renderState.lastWaiting = false;
}

function updateFastButton(fastMode) {
  if (!els.btnFast) return;
  els.btnFast.textContent = fastMode ? '加速：开' : '加速：关';
  els.btnFast.setAttribute('aria-pressed', fastMode ? 'true' : 'false');
}

function startNewGame() {
  const name = els.playerName.value.trim() || '玩家';
  const count = Number(document.querySelector('input[name="player-count"]:checked')?.value ?? 6);
  resetRenderState();
  showScreen('game');
  engine.start(name, count);
  setTimeout(() => showRoleDialog(els.roleDialog, engine.getHuman()), 400);
}

let skipResultCloseHandler = false;

function backToLobby() {
  skipResultCloseHandler = true;
  els.resultDialog.close();
  resetRenderState();
  engine.reset();
  showScreen('lobby');
  skipResultCloseHandler = false;
}

function dismissResultDialog() {
  els.resultDialog.close();
  renderState.resultDismissed = true;
  if (renderState.lastSnapshot) {
    renderPostGamePanel(renderState.lastSnapshot);
  }
}

function renderPostGamePanel(snapshot) {
  const postGame = buildPostGameUI({
    onPlayAgain: () => {
      els.resultDialog.close();
      startNewGame();
    },
    onBackLobby: backToLobby,
    onShowResult: () => showResultDialog(els.resultDialog, snapshot),
  });
  els.actionPanel.innerHTML = postGame.html;
  postGame.bind(els.actionPanel);
}

function render(snapshot) {
  renderState.lastSnapshot = snapshot;
  const { phase, round, isNight, log, waitingForHuman, humanPlayer, fastMode } = snapshot;

  els.phaseIcon.textContent = isNight ? '🌙' : '☀️';
  els.phaseText.textContent = getPhaseLabel(phase, round, isNight);
  els.phaseBadge.classList.toggle('night', isNight);
  els.phaseBadge.classList.toggle('day', !isNight);
  els.roundLabel.textContent = `回合 ${round}`;
  updateFastButton(fastMode);

  if (phase === PHASES.GAME_OVER) {
    renderPlayerRing(els.playerRing, snapshot, { selectableIds: [] });
    renderState.logLen = renderLog(els.gameLog, log, renderState.logLen);
    updateCenterHint(els.centerHint, snapshot);

    if (!renderState.resultShown) {
      renderState.resultShown = true;
      showResultDialog(els.resultDialog, snapshot);
    }

    if (renderState.resultDismissed || !els.resultDialog.open) {
      renderPostGamePanel(snapshot);
    } else {
      els.actionPanel.innerHTML = '<p class="action-placeholder">查看结算，或选择后续操作</p>';
    }
    return;
  }

  const action = buildActionUI(snapshot, (payload) => engine.resolveHumanAction(payload));
  const selectableIds = action.selectableIds ?? engine.getSelectableTargetIds();

  const phaseOrWaitChanged = phase !== renderState.lastPhase || waitingForHuman !== renderState.lastWaiting;
  if (phaseOrWaitChanged) {
    els.actionPanel.innerHTML = action.html;
    if (action.bind) action.bind(els.actionPanel);
    renderState.lastPhase = phase;
    renderState.lastWaiting = waitingForHuman;
  } else if (phase === PHASES.NIGHT_WITCH && waitingForHuman) {
    els.actionPanel.innerHTML = action.html;
    if (action.bind) action.bind(els.actionPanel);
  }

  els.actionPanel.classList.toggle('active-turn', waitingForHuman && humanPlayer?.alive);

  renderPlayerRing(els.playerRing, snapshot, {
    selectableIds,
    onSelectTarget: (id) => handleTableSelect(snapshot, id, engine),
  });

  renderState.logLen = renderLog(els.gameLog, log, renderState.logLen);

  if (els.seerPanel) {
    const showSeer = humanPlayer?.role === 'seer';
    els.seerPanel.hidden = !showSeer;
    if (showSeer) renderSeerHistory(els.seerHistory, snapshot.humanSeerHistory);
  }

  if (els.wolfHint) {
    const mates = snapshot.wolfTeammates ?? [];
    if (humanPlayer && humanPlayer.role === 'werewolf' && humanPlayer.alive && mates.length) {
      els.wolfHint.hidden = false;
      els.wolfHint.textContent = `狼队友：${mates.map((m) => m.name).join('、')}`;
    } else {
      els.wolfHint.hidden = true;
    }
  }

  if (els.votePanel) {
    renderVoteResult(els.voteResult, snapshot.lastVoteResult);
    els.votePanel.hidden = !snapshot.lastVoteResult?.tally?.length;
  }

  updateCenterHint(els.centerHint, snapshot);
}

els.lobbyForm.addEventListener('submit', (e) => {
  e.preventDefault();
  startNewGame();
});

els.btnRole.addEventListener('click', () => {
  showRoleDialog(els.roleDialog, engine.getHuman());
});

els.roleClose.addEventListener('click', () => els.roleDialog.close());

els.btnFast?.addEventListener('click', () => {
  engine.setFastMode(!engine.fastMode);
});

els.btnRestart.addEventListener('click', () => {
  if (confirm('确定要结束当前对局吗？')) {
    backToLobby();
  }
});

els.btnPlayAgain.addEventListener('click', () => {
  els.resultDialog.close();
  startNewGame();
});

els.btnBackLobby?.addEventListener('click', backToLobby);

els.btnReviewTable?.addEventListener('click', dismissResultDialog);

els.resultDialog.addEventListener('close', () => {
  if (skipResultCloseHandler) return;
  if (renderState.lastSnapshot?.phase === PHASES.GAME_OVER && !renderState.resultDismissed) {
    renderState.resultDismissed = true;
    renderPostGamePanel(renderState.lastSnapshot);
  }
});

engine.onChange(render);

const savedName = localStorage.getItem('werewolf-name');
els.playerName.value = savedName || '旅人';
els.playerName.addEventListener('change', () => {
  localStorage.setItem('werewolf-name', els.playerName.value.trim());
});

updateFastButton(engine.fastMode);

} // end init guard
