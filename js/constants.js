(function (W) {
  if (W.WerewolfConsts) return;

const ROLES = {
  WEREWOLF: 'werewolf',
  SEER: 'seer',
  WITCH: 'witch',
  HUNTER: 'hunter',
  VILLAGER: 'villager',
};

const ROLE_META = {
  [ROLES.WEREWOLF]: {
    name: '狼人',
    camp: 'wolf',
    desc: '每晚与同伴共同选择一名玩家出局。当狼人数量不少于好人时，狼人阵营获胜。',
    color: '#ff006e',
    icon: '🐺',
  },
  [ROLES.SEER]: {
    name: '预言家',
    camp: 'good',
    desc: '每晚可查验一名玩家的身份（狼人或好人）。',
    color: '#00ffff',
    icon: '🔮',
  },
  [ROLES.WITCH]: {
    name: '女巫',
    camp: 'good',
    desc: '拥有一瓶解药和一瓶毒药，整局各能使用一次。夜晚可知悉狼刀目标。',
    color: '#a855f7',
    icon: '🧪',
  },
  [ROLES.HUNTER]: {
    name: '猎人',
    camp: 'good',
    desc: '被投票出局或在夜晚被杀害时，可开枪带走一名玩家（被毒杀除外）。',
    color: '#ffb000',
    icon: '🎯',
  },
  [ROLES.VILLAGER]: {
    name: '村民',
    camp: 'good',
    desc: '没有特殊技能。白天通过讨论与投票找出狼人。',
    color: '#8b9dc3',
    icon: '👤',
  },
};

const PHASES = {
  NIGHT_WOLF: 'night_wolf',
  NIGHT_SEER: 'night_seer',
  NIGHT_WITCH: 'night_witch',
  NIGHT_RESOLVE: 'night_resolve',
  DAY_ANNOUNCE: 'day_announce',
  DAY_HUNTER: 'day_hunter',
  DAY_DISCUSS: 'day_discuss',
  DAY_VOTE: 'day_vote',
  DAY_RESOLVE: 'day_resolve',
  GAME_OVER: 'game_over',
};

const AI_NAMES = [
  '阿岚', '北野', '陈默', '冬青', '方仪', '顾言', '韩澈', '江晚',
  '林溪', '莫离', '南笙', '沈砚', '唐糖', '温言', '夏目', '云舒',
];

const ROLE_DISTRIBUTION = {
  6: [
    ROLES.WEREWOLF, ROLES.WEREWOLF,
    ROLES.SEER, ROLES.WITCH, ROLES.HUNTER, ROLES.VILLAGER,
  ],
  8: [
    ROLES.WEREWOLF, ROLES.WEREWOLF,
    ROLES.SEER, ROLES.WITCH, ROLES.HUNTER,
    ROLES.VILLAGER, ROLES.VILLAGER, ROLES.VILLAGER,
  ],
};

function isWolf(role) {
  return role === ROLES.WEREWOLF;
}

function isGood(role) {
  return !isWolf(role);
}

function campOf(role) {
  return ROLE_META[role]?.camp ?? 'good';
}

W.WerewolfConsts = {
  ROLES, ROLE_META, PHASES, AI_NAMES, ROLE_DISTRIBUTION, isWolf, isGood, campOf,
};
})(window);
