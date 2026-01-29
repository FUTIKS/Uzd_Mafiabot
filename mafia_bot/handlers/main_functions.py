import re
import time
import random
import asyncio
from typing import Counter
from dispatcher import bot
from threading import Lock
from datetime import timedelta
from django.db import transaction
from aiogram.types import Message
from django.db.models import F as DF
from aiogram.enums import ChatMemberStatus
from core.constants import ROLE_EMOJI, ROLES_BY_COUNT,ROLES_CHOICES, ACTIONS
from mafia_bot.models import Game, GameSettings,User,MostActiveUser, UserRole
from aiogram.types import ChatPermissions,ChatMemberAdministrator, ChatMemberOwner
from mafia_bot.utils import games_state, last_wishes,game_tasks, active_role_used,writing_allowed_groups
from mafia_bot.buttons.inline import cart_inline_btn, doc_btn, com_inline_btn, don_inline_btn, elf_inline_btn, mafia_inline_btn, adv_inline_btn, spy_inline_btn,  action_inline_btn,use_hero_inline_btn

lock = Lock()
ROLE_LABELS = dict(ROLES_CHOICES)


MAFIA_ROLES = {
    "don", "mafia", "adv", "spy", "journalist"
}

SOLO_ROLES = {
    "killer", "ninja", "snowball", "clone", "drunk",
    "mermaid", "traveler", "fraud", "kam", "suid",
    "rage", "vampireold"
}

PEACE_ROLES = {
    "peace", "doc", "nurse", "daydi", "com", "serg",
    "lover", "cooker", "rich", "elf",
    "vampire_hunter", "nogiron", "ghost"
}
NIGHT_ACTION_ROLES = {
    # Peace
    "doc",  "daydi", "com", "lover",
    "cooker", "rich", "elf", "vampire_hunter",

    # Mafia
    "don", "mafia", "adv", "spy", "journalist",

    # Solo
    "killer", "ninja", "snowball", "clone",
    "drunk", "mermaid", "traveler", "fraud",
    "rage", "vampireold",
}

LINK_RE = re.compile(
    r"("
    r"(?:(?:https?://)|(?:www\.))"                 # http(s) or www
    r"|(?:t\.me/|telegram\.me/|tg://)"             # telegram links
    r"|(?:@[\w\d_]{4,})"                           # @first_name
    r"|(?:[a-z0-9-]+\.)+(?:com|net|org|ru|uz|io|me|app|xyz|info|biz|co|tv|online)\b"  # domains
    r")",
    re.IGNORECASE
)
WINNER_LABEL = {
    "peace": "👨🏼  Tinch axoli",
    "mafia": "🤵🏻 Mafialar",
    "solo": "🎩  Yakka rollar",
}

ROLE_TEAM = {
    # 🟢 PEACE SIDE
    "peace": "peace",
    "doc": "peace",
    "nurse": "peace",
    "com": "peace",
    "serg": "peace",
    "daydi": "peace",
    "lover": "peace",
    "cooker": "peace",
    "rich": "peace",
    "elf": "peace",
    "vampire_hunter": "peace",
    "nogiron": "peace",
    "ghost": "peace",

    # 🔴 MAFIA SIDE
    "don": "mafia",
    "mafia": "mafia",
    "adv": "mafia",
    "spy": "mafia",
    "journalist": "mafia",

    # 🟡 SOLO / CHAOS
    "killer": "solo",
    "ninja": "solo",
    "snowball": "solo",
    "clone": "solo",
    "drunk": "solo",
    "mermaid": "solo",
    "traveler": "solo",
    "fraud": "solo",
    "kam": "solo",
    "suid": "solo",
    "rage": "solo",
    "vampireold": "solo",
}


ROLE_NIGHT_ROUTER = {
    "doc": lambda tg_id, g, players, day: (
        ACTIONS.get("doc_heal"),
        doc_btn(players=players, doctor_id=tg_id, game_id=g.id, chat_id=g.chat_id, day=day)
    ),
    "daydi": lambda tg_id, g, players, day: (
        ACTIONS.get("daydi_watch"),
        action_inline_btn("daydi", tg_id, players, g.id, g.chat_id, day)
    ),
    "com": lambda tg_id, g, players, day: (
        ACTIONS.get("com_deside"),
        com_inline_btn(g.id, g.chat_id, day=day)
    ),
    "rich": lambda tg_id, g, players, day: (
        ACTIONS.get("rich"),
        action_inline_btn("rich", tg_id, players, g.id, g.chat_id, day)
    ),
    "killer": lambda tg_id, g, players, day: (
        ACTIONS.get("killer_kill"),
        action_inline_btn("killer", tg_id, players, g.id, g.chat_id, day)
    ),
    "lover": lambda tg_id, g, players, day: (
        ACTIONS.get("lover_block"),
        action_inline_btn("lover", tg_id, players, g.id, g.chat_id, day)
    ),
    "cooker": lambda tg_id, g, players, day: (
        ACTIONS.get("cooker_spell"),
        action_inline_btn("cooker", tg_id, players, g.id, g.chat_id, day)
    ),
    "don": lambda tg_id, g, players, day: (
        ACTIONS.get("don_kill"),
        don_inline_btn(players, g.id, g.chat_id, tg_id, day)
    ),
    "mafia": lambda tg_id, g, players, day: (
        ACTIONS.get("mafia_vote"),
        mafia_inline_btn(players, g.id, day)
    ),
    "adv": lambda tg_id, g, players, day: (
        ACTIONS.get("adv_mask"),
        adv_inline_btn(players, g.id, g.chat_id, day)
    ),
    "spy": lambda tg_id, g, players, day: (
        ACTIONS.get("spy_check"),
        spy_inline_btn(players, g.id, g.chat_id, day, tg_id)
    ),
    "mermaid": lambda tg_id, g, players, day: (
        ACTIONS.get("mermaid_kill"),
        action_inline_btn("mermaid", tg_id, players, g.id, g.chat_id, day)
    ),
    "ninja": lambda tg_id, g, players, day: (
        ACTIONS.get("ninja_kill"),
        action_inline_btn("ninja", tg_id, players, g.id, g.chat_id, day)
    ),
    "snowball": lambda tg_id, g, players, day: (
        ACTIONS.get("snowball_kill"),
        action_inline_btn("snowball", tg_id, players, g.id, g.chat_id, day)
    ),
    
    "fraud": lambda tg_id, g, players, day: (
        ACTIONS.get("fraud_steal_vote"),
        action_inline_btn("fraud", tg_id, players, g.id, g.chat_id, day)
    ),
    "rage": lambda tg_id, g, players, day: (
        ACTIONS.get("rage_mark"),
        action_inline_btn("rage", tg_id, players, g.id, g.chat_id, day)
    ),
    "journalist": lambda tg_id, g, players, day: (
        ACTIONS.get("journalist_check"),
        action_inline_btn("journalist", tg_id, players, g.id, g.chat_id, day)
    ),
    "elf": lambda tg_id, g, players, day: (
        ACTIONS.get("elf_attack"),
        elf_inline_btn(players, g.id, g.chat_id, day, tg_id)
    ),
    "vampirehunter": lambda tg_id, g, players, day: (
        ACTIONS.get("vampirehunter_kill"),
        action_inline_btn("vampirehunter", tg_id, players, g.id, g.chat_id, day)
    ),
    "traveler": lambda tg_id, g, players, day: (
        ACTIONS.get("traveler_copy"),
        action_inline_btn("traveler", tg_id, players, g.id, g.chat_id, day)
    ),

    "vampireold": lambda tg_id, g, players, day: (
        ACTIONS.get("vampire_old_kill"),
        action_inline_btn("vampireold", tg_id, players, g.id, g.chat_id, day)
    ),

    "drunk": lambda tg_id, g, players, day: (
        ACTIONS.get("drunk_action"),
        action_inline_btn("drunk", tg_id, players, g.id, g.chat_id, day)
    ),

    "clone": lambda tg_id, g, players, day: (
        ACTIONS.get("clone"),
        action_inline_btn("clone", tg_id, players, g.id, g.chat_id, day)
    ),

  
}

async def send_night_action(tg_id, role, game_id, game, users_after_night, day):
    game_data = games_state.get(game_id, {})
    night_action = game_data.get("night_actions", {})
    effects = game_data.get("effects", {})
    if night_action.get("lover_block_target") == tg_id:
        return
    if tg_id in effects.get("blocked", {}):
        return
    role = game_data.get("temp_roles", {}).get(tg_id) or role
    if role in ("peace","serg","kam","suid","nurse","nogiron","ghost"):
        return

    handler = ROLE_NIGHT_ROUTER.get(role)
    if not handler:
        return

    text, markup = handler(tg_id, game, users_after_night, day)

    await send_safe_message(
        chat_id=tg_id,
        text=text,
        reply_markup=markup
    )


async def send_night_actions_to_all( game_id, game,players,day):
    game_data = games_state.get(game_id, {})
    roles_map = game_data.get("roles", {})

    tasks = []
    for user in players:
        tg_id = user.get("tg_id")
        role = roles_map.get(tg_id)
        
        tasks.append(asyncio.create_task(
            send_night_action( tg_id, role, game_id, game,players,day)
        ))

    await asyncio.gather(*tasks, return_exceptions=True)


def init_game(game_id: int, chat_id: int | None = None):
    with lock:
        if game_id in games_state:
            return
        max_players = 30
        game_settings = GameSettings.objects.filter(group_id=int(chat_id)).first()
        if game_settings and game_settings.begin_instance:
            max_players = game_settings.number_of_players if game_settings else max_players
       

        games_state[game_id] = {
            "meta": {
                "game_id": game_id,
                "chat_id": chat_id,
                "created_at": int(time.time()),
                "phase": "lobby",
                "day": 0,
                "night": 0,
                "message_allowed":"yes",
                "team_chat_open":"no",
                "max_players": max_players,
                "is_active_game": False,
            },
            "runtime": {
                "night_event": None,
                "pending_night": set(),
                "hang_event": None,
                "pending_hang": set(),
                "confirm_event": None,
                "pending_confirm": set(),
             },
            "afk": {
                "missed_nights": {},   # {tg_id: count}
                "kicked": set(),       # kicked users log
            },

            "allowed_to_send_message":[] ,
            "players": [],
            "users_map": {},
            "alive": [],
            "dead": [],
            "left": [],
            "hanged": [],

            "roles": {},
            "team": {},

            "hero": {
                "has": set(),
                "used": set(),
            },

            "limits": {
                "doc_self_heal_used": set(),
                "traitor_transformed": set(),
            },

            "effects": {
                "protected": {},
                "blocked": {},
                "silenced": {},
                "poisoned": {},
                "no_hang": {},
                "advokat_masked": {},
            },

            "visits": {
                "log": [],
                "invisible_visitors": set(),
            },

            "kills": {
                "shooted": {},
                "hanged": set(),
                "special": set(),
            },
            "rage_marks":[],
            "temp_roles": {},

            "night_actions": {
                "don_kill_target": None,
                "mafia_vote": [],

                "doc_target": None,
                "com_check_target": None,
                "com_shoot_target": None,
                "mermaid_target":None,

                "daydi_house": None,
                "daydi_seen": [],
                "drunk_target": None,
                "vampire_old_target": None,
                "vampire_hunter_target": None,
                "fraud_target": None,
                "killer_target":[],
                "traveler_target": None,
                
                "elf_target": None,
                "journalist_house": None,
                "clone_target": None,
                "journalist_seen": [],

                "lover_block_target": None,

                "cooker_target": None,
                "advokat_target": None,
                "spy_target": None,
                
                "ninja_target": None,
                
                "snowball_target": None,
                "hero_targets":{},
                "hero_used":{},
                
            },

            "day_actions": {
                "votes": [],
                "hang_yes":[],
                "hang_no":[],
                "fraud_target": None,
                
                "hang_confir_msg_id": None,
                "last_hanged": None,
                "kamikaze_trigger": None,
                "kamikaze_take": None,
            },
        }

BAD_GUYS = {"mafia","don"}


async def punish_afk_night_players(game_id):
    game = games_state.get(game_id)
    if not game:
        return

    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    chat_id = game.get("meta", {}).get("chat_id")

    runtime = game.get("runtime", {})
    pending = set(runtime.get("pending_night", set()))  # tun tugaganda kim qolgan bo'lsa - action qilmadi

    afk = game.setdefault("afk", {})
    missed = afk.setdefault("missed_nights", {})
    kicked = afk.setdefault("kicked", set())

    # pending ichida o'lganlar bo'lib qolmasin
    pending = {pid for pid in pending if pid in alive}

    # bosmaganlarga +1
    for pid in pending:
        missed[pid] = missed.get(pid, 0) + 1

    # bosganlar reset (night_action role bo'lsa)
    for pid in list(missed.keys()):
        if pid in alive and roles.get(pid) in NIGHT_ACTION_ROLES and pid not in pending:
            missed[pid] = 0

    # 2 marta bo'lsa kick
    to_kick = [pid for pid, cnt in missed.items() if cnt >= 2 and pid in alive]

    if not to_kick:
        return

    # userlarni 1 ta query bilan olish
    users_qs = game.get("users_map", {})
    night_text= []
    for pid in to_kick:
        alive.discard(pid)
        kicked.add(pid)

        # state update
        if pid in game["alive"]:
            game["alive"].remove(pid)
        if pid not in game["dead"]:
            game["dead"].append(pid)
        if pid not in game.get("left", []):
            game.setdefault("left", []).append(pid)

        # counter reset
        missed[pid] = 0

        # guruhga xabar
        if chat_id:
            user = users_qs.get(pid)
            name = user.get("first_name") if user else str(pid)
            role = roles.get(pid, "Noma'lum")
            if role == "don":
                new_don_id = promote_new_don_if_needed(game)
                if new_don_id:
                    await notify_new_don( game,new_don_id)
                    await send_safe_message(
                        chat_id=chat_id,
                        text=f"🤵🏻 Don vafot etdi.\nMafialardan biri endi yangi Don "
                                )
            elif role == "com":
                new_com_id = promote_new_com_if_needed(game)
                if new_com_id:
                    await notify_new_com(  new_com_id)
                    await send_safe_message(
                                chat_id=chat_id,
                                text=f"🕵🏻‍♂ Komissar vafot etdi.\nYangi Komissar tayinlandi."
                            )
            elif role == "doc":
                new_doc_id = promote_new_doc_if_needed(game)
                if new_doc_id:
                    await notify_new_doc(new_doc_id)
                    await send_safe_message(
                                chat_id=chat_id,
                                text=f"🩺 Doktor vafot etdi.\nYangi Doktor tayinlandi."
                            )
                
            role_label = ROLE_LABELS.get(role, role)
            night_text.append(f"Tunda {role_label} <a href='tg://user?id={pid}'>{name}</a> vahshiylarcha o‘ldirildi...\nU o‘lim oldidan shunday so‘z qoldirdi:\n'Men o‘yin paytida boshqa uxlamayma-a-a-a-a-a-an!'")
    try:
        await send_safe_message(
        chat_id=int(chat_id),
        text="\n\n".join(night_text),
        parse_mode="HTML"
        )
    except Exception:
        pass






def prepare_hang_pending(game_id:int):
    game = games_state.get(game_id)
    if not game:
        return

    alive = set(game.get("alive", []))

    game.setdefault("runtime", {})
    game["runtime"]["pending_hang"] = set(int(x) for x in alive)
    game["runtime"]["hang_event"] = asyncio.Event()

    if not alive:
        game["runtime"]["hang_event"].set()

def mark_hang_done(game_id, voter_id: int):
    
    game = games_state.get(game_id)
    if not game:
        return

    runtime = game.get("runtime", {})
    pending = runtime.get("pending_hang")
    event = runtime.get("hang_event")

    if not pending or not event:
        return

    pending.discard(int(voter_id))

    if len(pending) == 0:
        event.set()


def prepare_night_pending(game_id: int):
    game = games_state.get(game_id)
    if not game:
        return

    roles = game.get("roles", {})
    alive = set(game.get("alive", []))

    pending = set()
    for tg_id in alive:
        role = roles.get(int(tg_id))
        if role in NIGHT_ACTION_ROLES:
            pending.add(int(tg_id))

    game.setdefault("runtime", {})
    game["runtime"]["pending_night"] = pending
    game["runtime"]["night_event"] = asyncio.Event()

    if not pending:
        game["runtime"]["night_event"].set()

def mark_night_action_done(game, tg_id: int):
    if not game:
        return

    runtime = game.get("runtime", {})
    pending = runtime.get("pending_night")
    event = runtime.get("night_event")

    if pending is None or event is None:
        return

    pending.discard(int(tg_id))

    if len(pending) == 0:
        event.set()

def prepare_confirm_pending(game_id: int, voted_user_id: int):
    game = games_state.get(game_id)
    if not game:
        return

    alive = set(int(x) for x in game.get("alive", []))

    # ✅ osilayotgan odam confirm bermaydi
    alive.discard(int(voted_user_id))

    game.setdefault("runtime", {})
    game["runtime"]["pending_confirm"] = alive
    game["runtime"]["confirm_event"] = asyncio.Event()

    if not alive:
        game["runtime"]["confirm_event"].set()
        
def mark_confirm_done(game_id, voter_id: int):
    game = games_state.get(game_id)

    runtime = game.get("runtime", {})
    pending = runtime.get("pending_confirm")
    event = runtime.get("confirm_event")

    if pending is None or event is None:
        return


    pending.discard(int(voter_id))

    if len(pending) == 0:
        event.set()



def get_most_voted_id(game_id: int):
    all_votes = games_state.get(game_id, {}).get("day_actions", {}).get("votes", [])
    if not all_votes:
        return False

    counts = Counter(all_votes)
    max_votes = max(counts.values())

    top_ids = [tg_id for tg_id, c in counts.items() if c == max_votes]

    if len(top_ids) == 1:
        return top_ids[0]

    return False

def can_hang(game_id: int) -> bool:
    game = games_state.get(game_id)
    if not game:
        return False

    yes = len(game["day_actions"].get("hang_yes", []))
    no = len(game["day_actions"].get("hang_no", []))
    if yes > no:
        return "yes" , yes, no
    else:
        return "no" , yes, no
    
def get_mafia_members(game_id):
    game = games_state.get(int(game_id), {})
    roles_map = game.get("roles", {})
    alive = set(game.get("alive", []))

    members = []
    for tg_id, role in roles_map.items():
        if tg_id in alive and role == "mafia":
            members.append(tg_id)
        if tg_id in alive and role == "don":
            members.append(tg_id)
        if tg_id in alive and role == "adv":
            members.append(tg_id)
        if tg_id in alive and role == "spy":
            members.append(tg_id)
    return members


def remove_prefix(text):
    return text.lstrip('@')

def parse_amount(text: str) -> int | None:
    if not text:
        return None

    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None

    raw = parts[1].strip()
    raw = raw.replace(" ", "").replace(",", "").replace(".", "")
    if not raw.isdigit():
        return None

    amount = int(raw)
    if amount <= 0:
        return None

    return amount


def role_icon(role_key):
    return ROLE_EMOJI.get(role_key, "❓")
    

def is_alive(game, tg_id: int) -> bool:
    return int(tg_id) in set(game.get("alive", []))



def find_game(game_id, tg_id,chat_id,user):
    init_game(game_id,chat_id)
    tg_id = int(tg_id)

    with lock:
        game = games_state[game_id]

        if tg_id in game["players"]:
            return {"message": "already_in"}
        max_players = game["meta"].get("max_players", 40)
        if len(game["players"]) >= max_players:
            return {"message": "full"}

        game["players"].append(tg_id)
        game["users_map"][tg_id]={"first_name":user.first_name,"protection":1 if user.protection>=1 else 0,"doc": 1 if user.docs>=1 else 0,"hang_protect": 1 if user.hang_protect>=1 else 0,"tg_id":tg_id,"hero":user.is_hero}
        game["alive"].append(tg_id)
        if len(game["players"])==max_players:
            return {"message": "full"}

    return {"message": "joined"}



def create_main_messages(game_id):
    tg_ids = games_state.get(game_id, {}).get("players", [])

    msg = "Ro'yxatdan o'tish boshlandi\n\nRo'yxatdan o'tganlar:\n"

    if not tg_ids:
        return msg + "\n\nJami 0ta odam"

    users_map = games_state.get(game_id, {}).get("users_map", {})
    
    count = 0
    for tg_id in tg_ids:
        user = users_map.get(tg_id)
        if not user:
            continue
        msg += f'<a href="tg://user?id={tg_id}">{user.get("first_name")}</a>, '
        count += 1

    msg += f"\n\nJami {count}ta odam"
    return msg




def night_reset(game_id: int):
    with lock:
        game = games_state.get(game_id)
        if not game:
            return False

        game["meta"]["phase"] = "night"
        game["meta"]["night"] += 1

        game["effects"]["protected"].clear()
        game["effects"]["blocked"].clear()
        game["effects"]["silenced"].clear()
        game["effects"]["poisoned"].clear()
        game["effects"]["no_hang"].clear()
        game["effects"]["advokat_masked"].clear()

        game["visits"]["log"].clear()
        game["visits"]["invisible_visitors"].clear()

        game["kills"]["shooted"].clear()
        game["kills"]["special"].clear()

        na = game["night_actions"]

        na["don_kill_target"] = None
        na["mafia_vote"].clear()

        na["doc_target"] = None
        na["com_check_target"] = None
        na["com_shoot_target"] = None
        na["mermaid_target"] = None

        na["daydi_house"] = None
        na["daydi_seen"].clear()

        na["drunk_target"] = None
        na["vampire_old_target"] = None
        na["vampire_hunter_target"] = None

        na["fraud_target"] = None
        na["traveler_target"] = None
        na["elf_target"] = None

        na["journalist_house"] = None
        na["journalist_seen"].clear()
        na["clone_target"] = None

        na["lover_block_target"] = None
        na["cooker_target"] = None
        na["killer_target"] = []
        na["advokat_target"] = None
        na["spy_target"] = None
        na["ninja_target"] = None
        na["snowball_target"] = None

        na["hero_targets"].clear()
        na["hero_used"].clear()

        rt = game["runtime"]
        rt["night_event"] = None
        rt["pending_night"].clear()

        return True



def day_reset(game_id: int):
    with lock:
        game = games_state.get(game_id)
        if not game:
            return False

        game["meta"]["phase"] = "day"
        game["meta"]["day"] += 1

        game["kills"]["hanged"].clear()
        game["temp_roles"].clear()


        da = game["day_actions"]
        da["votes"].clear()
        da["hang_yes"].clear()
        da["hang_no"].clear()
        da["fraud_target"] = None

        da["hang_confir_msg_id"] = None
        da["last_hanged"] = None
        da["kamikaze_trigger"] = None
        da["kamikaze_take"] = None

        rt = game["runtime"]
        rt["hang_event"] = None
        rt["pending_hang"].clear()
        rt["confirm_event"] = None
        rt["pending_confirm"].clear()

        return True


def shuffle_roles(game_id) -> bool:
    game = games_state.get(game_id)
    if not game:
        return False

    players = game.get("players", [])
    num_players = len(players)

    base_roles = ROLES_BY_COUNT.get(num_players)
    if not base_roles:
        return False

    roles = base_roles.copy()
    random.shuffle(roles)

    roles_map = {}
    fixed_players = []

    for tg_id in players:
        user = User.objects.filter(telegram_id=tg_id).first()
        if not user:
            continue

        user_roles = UserRole.objects.filter(user_id=user.id, quantity__gt=0)
        if not user_roles.exists():
            continue

        chosen_ur = None
        for ur in user_roles:
            if ur.role_key in roles:
                chosen_ur = ur
                break

        if not chosen_ur:
            continue

        roles_map[tg_id] = chosen_ur.role_key
        fixed_players.append(tg_id)

        UserRole.objects.filter(id=chosen_ur.id, role_key=chosen_ur.role_key, quantity__gt=0).update(quantity=DF("quantity") - 1)
        UserRole.objects.filter(id=chosen_ur.id, role_key=chosen_ur.role_key, quantity__lte=0).delete()
        active_role_used.append(tg_id)

        try:
            roles.remove(chosen_ur.role_key)
        except ValueError:
            pass

    remaining_players = [p for p in players if p not in fixed_players]
    random.shuffle(remaining_players)

    for tg_id, role in zip(remaining_players, roles):
        roles_map[tg_id] = role

    game["roles"] = roles_map
    return True


def add_visit(game: dict, visitor_id: int, house_id: int, invisible: bool = False):
    with lock:
        if not game:
            return

        game["visits"]["log"].append((int(visitor_id), int(house_id)))

        if invisible:
            game["visits"]["invisible_visitors"].add(int(visitor_id))





def check_bot_rights(bot_member) -> str | bool:
    message_text = (
        "⚠️ Botga yetarli admin huquqlari berilmagan!\n"
        "Salom! Men Mafia o'yinini rasmiy botiman.\n\n"
        "Quyidagi ruxsatlar kerak:\n"
    )

    # Bot admin emas bo‘lsa — hammasini so‘raymiz
    if bot_member.status not in ("administrator", "creator"):
        return (
            message_text +
            "☑️ Admin qilish\n"
            "☑️ Xabarlarni o‘chirish\n"
            "☑️ A’zolarni cheklash\n"
            "☑️ Xabarlarni qadash\n"
        )

    # Owner bo‘lsa hammasiga ruxsat bor
    if isinstance(bot_member, ChatMemberOwner):
        return False

    # Administrator bo‘lsa — rights tekshiramiz
    if isinstance(bot_member, ChatMemberAdministrator):
        no_all_rights = False

        if not bot_member.can_delete_messages:
            message_text += "☑️ Xabarlarni o‘chirish\n"
            no_all_rights = True

        if not bot_member.can_restrict_members:
            message_text += "☑️ A’zolarni cheklash\n"
            no_all_rights = True

        if not bot_member.can_pin_messages:
            message_text += "☑️ Xabarlarni qadash\n"
            no_all_rights = True

        if not no_all_rights:
            return False

        return message_text

    return False

def get_mafia_kill_target(night_actions):
    don_target = night_actions.get("don_kill_target")
    mafia_votes = night_actions.get("mafia_vote", [])  # list

    targets = mafia_votes.copy()

    if don_target:
        targets.append(don_target)  # 1x
        targets.append(don_target)  # 2x ✅

    if not targets:
        return None

    counts = Counter(targets)
    max_votes = max(counts.values())
    top = [t for t, c in counts.items() if c == max_votes]

    # agar durang bo'lsa None
    if len(top) != 1:
        return don_target

    return top[0]

def get_first_name_from_players(tg_id):
    user = User.objects.filter(telegram_id=tg_id).only("telegram_id", "first_name").first()
    if user:
        return user.first_name
    return str(tg_id)

def has_link(text: str) -> bool:
    if not text:
        return False
    return bool(LINK_RE.search(text))



def role_label(role_key: str):
    return ROLE_LABELS.get(role_key, role_key or "")
        
        
def kill(game, tg_id: int):
    if not tg_id:
        return
    if not game:
        return
    tg_id = int(tg_id)
    if tg_id in game["alive"]:
        game["alive"].remove(tg_id)
    if tg_id not in game["dead"]:
        game["dead"].append(tg_id)
    
def compute_daydi_seen(game):
    night_actions = game["night_actions"]

    daydi_house = night_actions.get("daydi_house")
    if not daydi_house:
        night_actions["daydi_seen"] = []
        return []

    daydi_house = int(daydi_house)
    invisible = game["visits"]["invisible_visitors"]
    visits = game["visits"]["log"]

    seen = []
    for visitor_id, house_id in visits:
        visitor_id = int(visitor_id)
        house_id = int(house_id)

        # Faqat daydi tanlagan uyga kelganlar
        if house_id != daydi_house:
            continue

        # Ko‘rinmaydigan visitorlar
        if visitor_id in invisible:
            continue

        # Uy egasini o‘zi ko‘rmaydi
        if visitor_id == daydi_house:
            continue

        if visitor_id not in seen:
            seen.append(visitor_id)

    night_actions["daydi_seen"] = seen
    return seen

def get_alive_role_id(game, role_key: str):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    for tg_id, r in roles.items():
        if r == role_key and tg_id in alive:
            return tg_id
    return None
    
def compute_journalist_seen(game):
    night_actions = game["night_actions"]

    journalist_house = night_actions.get("journalist_house")
    if not journalist_house:
        night_actions["journalist_seen"] = []
        return []

    journalist_house = int(journalist_house)
    invisible = game["visits"]["invisible_visitors"]
    visits = game["visits"]["log"]

    seen = []
    for visitor_id, house_id in visits:
        visitor_id = int(visitor_id)
        house_id = int(house_id)
        role = game["roles"].get(visitor_id)

        # Faqat daydi tanlagan uyga kelganlar
        if house_id != journalist_house:
            continue

        # Ko‘rinmaydigan visitorlar
        if visitor_id in invisible:
            continue

        # Uy egasini o‘zi ko‘rmaydi
        if visitor_id == journalist_house:
            continue
        
        
        if role in MAFIA_ROLES:
            continue

        if visitor_id not in seen:
            seen.append(visitor_id)

    night_actions["journalist_seen"] = seen
    return seen



def get_alive_role_ids(game, role_key: str):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    return [tg_id for tg_id, r in roles.items() if r == role_key and tg_id in alive]


def get_visible_role_for_com(game, target_id: int, users_map=None) -> str:
    roles = game.get("roles", {})
    effects = game.get("effects", {})

    real_role = roles.get(int(target_id))

    if not real_role:
        return "peace"

    # 1) advokat mask (agar target mafiyadan bo'lsa)
    adv_masked = effects.get("advokat_masked", {})
    if int(target_id) in adv_masked:
        return "peace"

    # 2) shop protection: mafia/solo bo'lsa tinch ko'rinsin
    if users_map:
        user = users_map.get(int(target_id))
        if user and user.get("docs", 0) > 0 and real_role in (MAFIA_ROLES | SOLO_ROLES):
            user_qs = User.objects.filter(telegram_id=int(target_id)).first()
            user["docs"] -= 1
            user_qs.docs -= 1
            user_qs.save(update_fields=["docs"])
            # Assuming there's a mechanism to save the updated user data back to the database or game state
            return "peace"

    return real_role


def promote_new_don_if_needed(game: dict):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))

    alive_don = any(roles.get(tg) == "don" for tg in alive)
    if alive_don:
        return None

    mafia_candidates = [
        tg for tg in alive
        if roles.get(tg) in ("mafia",)   # faqat mafia ichidan
    ]

    if not mafia_candidates:
        return None

    new_don_id = mafia_candidates[0]  # xohlasangiz random ham qilsa bo'ladi
    roles[new_don_id] = "don"
    game["roles"] = roles
    return new_don_id


async def notify_new_don(game: dict, new_don_id: int):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    user_map = game.get("users_map", {})    

    mafia_members = [
        tid for tid in alive
        if roles.get(tid) in MAFIA_ROLES
    ]   
    
    await send_safe_message(
        chat_id=int(new_don_id),
        text="🤵🏻 Sizning Don vafot etdi.\nEndi siz yangi Don bo'ldingiz!",
    )

    for member_id in mafia_members:
        if member_id == int(new_don_id):
            continue
        try:
            user = user_map.get(int(new_don_id))
            await send_safe_message(
                chat_id=int(member_id),
                text=f"🤵🏻 Sizning yangi Don: <a href='tg://user?id={new_don_id}'>{user.get('first_name')}</a>",
                parse_mode="HTML"
            )
        except Exception:
            pass




def promote_new_com_if_needed(game: dict):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))

    alive_com = any(roles.get(tg) == "com" for tg in alive)
    if alive_com:
        return None

    # serg tirik bo'lsa o'sha komissar bo'ladi
    serg_id = next((tg for tg in alive if roles.get(tg) == "serg"), None)
    if not serg_id:
        return None

    roles[int(serg_id)] = "com"
    game["roles"] = roles
    return int(serg_id)

async def notify_new_com( new_com_id: int):
    # serjantning o'ziga
    if not new_com_id:
        return
    try:
        await send_safe_message(
            chat_id=int(new_com_id),
            text="🕵🏻‍♂ Komissar vafot etdi.\nEndi siz Komissar bo'ldingiz!",
        )
        
    except Exception:
        pass

def promote_new_doc_if_needed(game: dict):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))

    alive_doc = any(roles.get(tg) == "doc" for tg in alive)
    if alive_doc:
        return None

    # serg tirik bo'lsa o'sha komissar bo'ladi
    nurse_id = next((tg for tg in alive if roles.get(tg) == "nurse"), None)
    if not nurse_id:
        return None

    roles[int(nurse_id)] = "doc"
    game["roles"] = roles
    return int(nurse_id)

async def notify_new_doc( new_doc_id: int):
    # serjantning o'ziga
    if not new_doc_id:
        return
    try:
        await send_safe_message(
            chat_id=int(new_doc_id),
            text="🕵🏻‍♂ Komissar vafot etdi.\nEndi siz Komissar bo'ldingiz!",
        )
        
    except Exception:
        pass

def clone_check_transform(game: dict):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    dead = set(game.get("dead", []))
    na = game.get("night_actions", {})

    clone_id = next((uid for uid, r in roles.items() if r == "clone"), None)
    if not clone_id or clone_id not in alive:
        return None

    target_id = na.get("clone_target")
    if not target_id:
        return None

    target_id = int(target_id)

    # Agar target shu tun o‘lgan bo‘lsa
    if target_id in dead:
        new_role = roles.get(target_id)
        if not new_role:
            return None

        roles[clone_id] = new_role
        game["roles"] = roles

        return clone_id, new_role

    return None



def traveler_copy_role(game: dict):
    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    night_actions = game.get("night_actions", {})
    effects = game.get("effects", {})

    traveler_id = next((uid for uid, r in roles.items() if r == "traveler" and uid in alive), None)
    if not traveler_id:
        return None

    target_id = night_actions.get("traveler_target")
    if not target_id:
        return None

    target_id = int(target_id)

    if target_id not in alive or target_id == traveler_id:
        return None

    target_role = roles.get(target_id)
    if not target_role:
        return None

    # Traveler vaqtincha rol oladi
    game.setdefault("temp_roles", {})[traveler_id] = target_role

    # Target bloklanadi (system bo‘yicha)
    effects["blocked"][target_id] = "traveler"

    return traveler_id, target_id, target_role


async def hero_day_actions(game_id: int):
    game = games_state.get(int(game_id))
    if not game:
        return

    users_map = game.get("users_map", {})
    roles = game.get("roles", {})
    meta = game.get("meta", {})
    chat_id = meta.get("chat_id")
    day = meta.get("day")

    for tg_id, user in users_map.items():
        tg_id = int(tg_id)
        if tg_id not in game.get("alive", []):
            continue

        is_hero = user.get("hero", False)
        if not is_hero:
            continue

        role = roles.get(tg_id)

        if role in ["don", "com", "ninja"]:
            await send_safe_message(
                chat_id=tg_id,
                text="🥷 O'z tanlovingizni qiling",
                reply_markup=use_hero_inline_btn(
                    game_id=game_id,
                    chat_id=chat_id,
                    day=day
                )
            )
        else:
            await send_safe_message(
                chat_id=tg_id,
                text="🥷 Siz geroy orqali faqat o'zingizni himoyalay olasiz."
            )

async def deny_kill(game, attacker_role, text):
    attacker_id = get_alive_role_id(game, attacker_role)
    if attacker_id:
        await send_safe_message(chat_id=int(attacker_id), text=text)



async def apply_night_actions(game_id: int):
    game = games_state.get(game_id)
    if not game:
        return

    game.setdefault("allowed_to_send_message", [])

    night_actions = game.get("night_actions", {})
    effects = game.get("effects", {})
    roles = game.get("roles", {})

    chat_id = game.get("meta", {}).get("chat_id")
    if not chat_id:
        return

    alive_ids = game.get("alive", [])
    alive_users_map = game.get("users_map", {})
    
    def uname(tg_id):
        user = alive_users_map.get(int(tg_id))
        return user.get("first_name") if user else str(tg_id)

    clone_check_transform(game)
    traveler_copy_role(game)
    protected = effects.setdefault("protected", {})

    doc_id = get_alive_role_id(game, "doc")
    if doc_id:
        doc_target = night_actions.get("doc_target")
        if doc_target and is_alive(game, doc_target):
            protected[int(doc_target)] = "doc"
    kill_intents = {}

    def add_intent(target_id, by_role, priority=1):
        if not target_id:
            return
        if isinstance(target_id, dict):
            return
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            return
        if not is_alive(game, target_id):
            return
        kill_intents.setdefault(target_id, []).append((by_role, priority))

    mafia_alive = any(roles.get(tg) in {"don", "mafia"} for tg in alive_ids)
    if mafia_alive:
        mafia_target = get_mafia_kill_target(night_actions)
        if  mafia_target:
            add_intent(mafia_target, "don", priority=1)
            mafia_ids = get_mafia_members(game_id)
            for mafia in mafia_ids:
                await send_safe_message(
            chat_id=int(mafia),
            text=f"Mafiyaning ovoz berishi yakunlandi\nMafialar {uname(mafia_target)} 💀 shavqatsizlarcha o'ldirdi."
        )

    killer_id = get_alive_role_id(game, "killer")
    if killer_id:
        for t in night_actions.get("killer_target", []):
            add_intent(t, "killer", priority=1)

    com_id = get_alive_role_id(game, "com")
    if com_id:
        add_intent(night_actions.get("com_shoot_target"), "com", priority=1)

    snowball_id = get_alive_role_id(game, "snowball")
    if snowball_id:
        add_intent(night_actions.get("snowball_target"), "snowball", priority=1)

    ninja_id = get_alive_role_id(game, "ninja")
    if ninja_id:
        add_intent(night_actions.get("ninja_target"), "ninja", priority=1)
    
    drunk_id = get_alive_role_id(game, "drunk")
    if drunk_id:
        add_intent(night_actions.get("drunk_target"), "drunk", priority=4)
        if random.random() < 0.4:
                add_intent(drunk_id, "💊 O'zi", priority=4)

    vamp_id = get_alive_role_id(game, "vampireold")
    if vamp_id:
        for t in night_actions.get("vampire_targets", []):
            add_intent(t, "vampireold", 3)

    vampir_hunter_id = get_alive_role_id(game, "vampirehunter")
    if vampir_hunter_id:
        t = night_actions.get("vampire_hunter_target")
        if t:
            add_intent(t, "vampirehunter", 1)
    
    
    mermaid_id = get_alive_role_id(game, "mermaid")
    if mermaid_id:
        t = night_actions.get("mermaid_target")
        if t :
            add_intent(t, "mermaid", 4)
            
    elf_id = get_alive_role_id(game, "elf")
    if elf_id:
        t = night_actions.get("elf_target")
        if t and roles.get(int(t)) not in PEACE_ROLES:
            add_intent(t, "elf", 4)
            
    cooker_id = get_alive_role_id(game, "cooker")
    if cooker_id:
        cooker_target = night_actions.get("cooker_target")
        if cooker_target and is_alive(game, cooker_target):
            if roles.get(int(cooker_target)) in PEACE_ROLES:
                protected[int(cooker_target)] = "cooker"
            else:
                add_intent(cooker_target, "cooker", priority=2)

    
  
   
     

    dead_tonight = []
    saved_tonight = []

    for target_id, intents in kill_intents.items():
        if target_id is None:
            continue
        intents.sort(key=lambda x: x[1], reverse=True)
        killer_by, pr = intents[0]
        role = roles.get(int(target_id))

        target_user = alive_users_map.get(int(target_id))
        hero_used = game.setdefault("hero_used", {})
        if target_user and target_user.get("hero", False):
            if not hero_used.get(target_id):
                hero_used[target_id] = True

                await send_safe_message(
                    chat_id=int(target_id),
                    text=(
                        "🥷 Sizni o'ldirishdi, lekin Geroy sizni bir marta o‘limdan saqlab qoldi!\n"
                        "Keyingi safar siz halok bo‘lasiz."
                    ),
                    parse_mode="HTML"
                )
                await send_safe_message(
                    chat_id=chat_id,
                    text=(
                        f"🥷 Geroy <a href='tg://user?id={target_id}'>{uname(target_id)}</a> ni o'limdan saqlab qoldi!"
                    ),
                    parse_mode="HTML"
                )
                continue
            
        if role == "ghost" and not killer_by == "ninja":
            killer_id = get_alive_role_id(game, killer_by)
            await deny_kill(game, killer_by,
                f"Siz Ghostni o'ldira olmaysiz!"
            )
            continue
        
        if role == "vampireold" and not killer_by == "vampirehunter":
            killer_id = get_alive_role_id(game, killer_by)
            await deny_kill(game, killer_by,
                f"Siz Vampirni o'ldira olmaysiz!"
            )
            continue
        
        if role == "mermaid" and  killer_by == "com":
            com_id = get_alive_role_id(game, "com")
            await deny_kill(game, "com",
                f"Siz Suv parisini o'ldira olmaysiz!"
            )
            continue
        
        if killer_by == "elf" and role in PEACE_ROLES:
            elf_id = get_alive_role_id(game, "elf")
            await deny_kill(game, "elf",
                f"Siz tinch aholini o'ldira olmaysiz!"
            )
            continue
        
        if target_id in protected:
            saved_tonight.append((target_id, protected[target_id], killer_by))
            continue
        
        if target_user and target_user.get("protection", 0) > 0:
            target_user_qs = User.objects.filter(telegram_id=int(target_id)).first()
            target_user["protection"] -= 1
            target_user_qs.protection -= 1
            target_user_qs.save(update_fields=["protection"])
            await send_safe_message(
                chat_id=int(chat_id),
                text=f"🛡️ Kimningdir himoyasi ishladi va tirik qoldi!"
            )
            saved_tonight.append((target_id, "himoya", killer_by))
            continue
        


        if role == "kam":
            killer_id = get_alive_role_id(game, killer_by)
            kill(game, killer_id)
            dead_tonight.append((killer_id, "kam"))

       
            
        kill(game, target_id)
        dead_tonight.append((target_id, killer_by))
    night_texts = []
    for target_id, killer_by in dead_tonight:
        target_role = roles.get(int(target_id))
        killer_role_label = role_label(killer_by)
        victim_role_label = role_label(target_role)

        night_texts.append(
                f"Tunda {victim_role_label} <a href='tg://user?id={target_id}'>{uname(target_id)}</a> "
                f"vahshiylarcha o'ldirildi...\n"
                f"Aytishlaricha u {killer_role_label} tomonidan o‘ldirilgan."
            )
            
        
        if target_role == "don":
            new_don_id = promote_new_don_if_needed(game)
            if new_don_id:
                await notify_new_don( game, new_don_id)
                await send_safe_message(
                    chat_id=chat_id,
                    text=f"🤵🏻 Don vafot etdi.\nMafialardan biri endi yangi Don "
                )
                
        if target_role == "com":
            new_com_id = promote_new_com_if_needed(game)
            if new_com_id:
                await notify_new_com( new_com_id)
                await send_safe_message(
                    chat_id=chat_id,
                    text=f"🕵🏻‍♂ Komissar vafot etdi.\nYangi Komissar tayinlandi."
                )
        if target_role == "doc":
            new_doc_id = promote_new_doc_if_needed(game)
            if new_doc_id:
                await notify_new_doc( new_doc_id)
                await send_safe_message(
                    chat_id=chat_id,
                    text=f"🩺 Doktor vafot etdi.\nYangi Doktor tayinlandi."
                )


        await send_safe_message(
            chat_id=int(target_id),
            text=(
                "<b>Sizni o'ldirishdi :(</b>\n"
                "Siz bu yerdan o'lim oldi xabar qoldirishingiz mumkin\n\n"
            ),
            parse_mode="HTML"
        )

        if int(target_id) not in game["allowed_to_send_message"]:
            game["allowed_to_send_message"].append(int(target_id))
            game_day = game.get('meta', {}).get('day', 1)
            last_wishes[int(target_id)] = (chat_id, game_day) 
            
    if night_texts:
        await send_safe_message(
            chat_id=chat_id,
            text="\n\n".join(night_texts),
            parse_mode="HTML"
        )           
            
    for target_id, protector_by, killer_by in saved_tonight:
        protector_role_label = role_label(protector_by)
        await send_safe_message(
                chat_id=int(target_id),
                text=(
                    f"<b>Sizni {protector_role_label} qutqardi!</b>\n"
                    "Siz tirik qoldingiz!"
                ),
                parse_mode="HTML"
            )
            
    
    com_id = get_alive_role_id(game, "com")
    serg_id = get_alive_role_id(game, "serg")
    com_check_target = night_actions.get("com_check_target")

    if com_id and com_check_target and is_alive(game, com_id):
        target_user = alive_users_map.get(int(com_check_target))
        target_name = target_user.get("first_name") if target_user else str(com_check_target)

        visible_role_key = get_visible_role_for_com(game, int(com_check_target), alive_users_map)
        visible_role_text = ROLE_LABELS.get(visible_role_key, "👨🏼 Tinch axoli")

        try:
            await send_safe_message(
                chat_id=int(com_check_target),
                text="Kimdir rolingizga qiziqdi..."
            )
            text = (
                    f"<a href='tg://user?id={com_check_target}'>{target_name}</a> - {visible_role_text}"
                )
            await send_safe_message(
                chat_id=com_id,
                text=text,
                parse_mode="HTML"
            )
            if serg_id and is_alive(game, serg_id):
                await send_safe_message(
                    chat_id=serg_id,
                    text=text,
                    parse_mode="HTML"
                )
        except Exception:
            pass
        
    spy_id = get_alive_role_id(game, "spy")
    spy_target = night_actions.get("spy_target")

    if spy_id and spy_target and is_alive(game, spy_id):
        target_user = alive_users_map.get(int(spy_target))
        target_name = target_user.get("first_name") if target_user else str(spy_target)

        real_role_key = roles.get(int(spy_target))
        real_role_text = ROLE_LABELS.get(real_role_key, "Unknown")

        try:
            await send_safe_message(
                chat_id=int(spy_target),
                text="Kimdir rolingizga qiziqdi..."
            )
            
            mafia_members = get_mafia_members(game_id)
            for member_id in mafia_members:
                if member_id == int(spy_id):
                    continue
                await send_safe_message(
                    chat_id=int(member_id),
                    text=(
                        f"Sizning ayg'oqchingiz <a href='tg://user?id={spy_target}'>{target_name}</a> ni "
                        f"tekshirdi va uning roli: {real_role_text}"
                    ),
                    parse_mode="HTML"
                )
            await send_safe_message(
                chat_id=int(spy_id),
                text=(
                    f"🦇 Siz tekshirgan odam:\n"
                    f"<a href='tg://user?id={spy_target}'>{target_name}</a>\n\n"
                    f"Uning roli: {real_role_text}"
                ),
                parse_mode="HTML"
            )
        except Exception:
            pass

    


    
    daydi_id = get_alive_role_id(game, "daydi")
    if daydi_id:
        daydi_seen = compute_daydi_seen(game)     
        daydi_house_id = night_actions.get("daydi_house")
        if daydi_house_id:
            daydi_house_id = int(daydi_house_id)
            house_owner = uname(daydi_house_id)

            lines = []
            for vid in daydi_seen:
                lines.append(f"<a href='tg://user?id={vid}'>{uname(vid)}</a>")

            if lines:
                text = (
                    f"🧙🏼‍♂️ Tunda siz shisha uchun "
                    f"<a href='tg://user?id={daydi_house_id}'>{house_owner}</a> ga keldingiz "
                    f"va u yerda {', '.join(lines)} ni ko'rdingiz."
                )
            else:
                text = (
                    f"🧙🏼‍♂️ Tunda siz "
                    f"<a href='tg://user?id={daydi_house_id}'>{house_owner}</a> dan shishalarni oldingiz va orqangizga qaytdingiz. Shubxali narsa sodir bo'lmadi."
                )

            await send_safe_message(
                chat_id=int(daydi_id),
                text=text,
                parse_mode="HTML"
            )
    journalist_id = get_alive_role_id(game, "journalist")
    if journalist_id:
        journalist_seen = compute_journalist_seen(game)     
        journalist_house_id = night_actions.get("journalist_house")
        if journalist_house_id:
            journalist_house_id = int(journalist_house_id)
            house_owner = uname(journalist_house_id)

            lines = []
            for vid in journalist_seen:
                lines.append(f"<a href='tg://user?id={vid}'>{uname(vid)}</a>")

            if lines:
                text = (
                    f"🗞 Tunda siz "
                    f"<a href='tg://user?id={journalist_house_id}'>{house_owner}</a> ga bordingiz va u yerda "
                    f"{', '.join(lines)} ni ko'rdingiz."
                )
            else:
                text = (
                    f"🗞 Tunda siz "
                    f"<a href='tg://user?id={journalist_house_id}'>{house_owner}</a> dan yangiliklar uchun ma'lumot to'pladingiz va orqangizga qaytdingiz. Shubxali narsa sodir bo'lmadi."
                )
            mafia_members = get_mafia_members(game_id)
            for member_id in mafia_members:
                if member_id == int(journalist_id):
                    continue
                await send_safe_message(
                    chat_id=int(member_id),
                    text=(
                        f"Sizning jurnalistingiz <a href='tg://user?id={journalist_id}'>"
                        f"{uname(journalist_id)}</a> bilan interview olishga bordi va u quyidagilarni ko'rdi:\n\n{text}"
                    ),
                    parse_mode="HTML"
                )
            await send_safe_message(
                chat_id=int(journalist_id),
                text=text,
                parse_mode="HTML"
            )
    lover_target = night_actions.get("lover_block_target")
    if lover_target and is_alive(game, lover_target):
        try:
            await send_safe_message(
                chat_id=int(lover_target),
                text="'Sen men bilan hamma narsani unut...', - deya kuyladi 💃🏼 <b>Ma'shuqa</b>",
                parse_mode="HTML"
            )
        except Exception:
            pass

      

                
def get_game_by_chat_id(chat_id: int):
    chat_id = int(chat_id)
    for game in games_state.values():
        if game.get("meta", {}).get("chat_id") == chat_id:
            return game
    return None    
                
def get_alive_teams(game):
    roles = game.get("roles", {})
    alive = game.get("alive", [])

    mafia = []
    peace = []
    solo = []

    for tg_id in alive:
        r = roles.get(tg_id)
        if r in MAFIA_ROLES:
            mafia.append(tg_id)
        elif r in PEACE_ROLES:
            peace.append(tg_id)
        elif r in SOLO_ROLES:
            solo.append(tg_id)

    return mafia, peace, solo
def check_game_over(game_id: int) -> str | None:
    game = games_state.get(game_id)
    if not game:
        return None

    alive = game.get("alive", [])
    if not alive:
        return "draw"

    mafia_ids, peace_ids, solo_ids = get_alive_teams(game)

    mafia = len(mafia_ids)
    peace = len(peace_ids)
    solo  = len(solo_ids)
    alive_count = mafia + peace + solo

    # =========================
    # 🔥 1. SOLO MAXSUS HOLATLAR
    # =========================

    # Faqat solo qolsa
    if solo > 0 and mafia == 0 and peace == 0:
        return "solo"

    # 1 peace + 1 solo
    if alive_count == 2 and peace == 1 and solo == 1:
        return "solo"

    # 1 mafia + 1 solo
    if alive_count == 2 and mafia == 1 and solo == 1:
        return "mafia"

    # =========================
    # 🔥 2. MAFIA PARITY QOIDASI (ENG MUHIM)
    # =========================
    # Mafia soni tinchlardan kam emas bo‘lsa — mafia yutadi
    if mafia > 0 and mafia >= peace and solo == 0:
        return "mafia"

    # 3 kishidan kam va mafia bor
    if alive_count < 3 and mafia > 0:
        return "mafia"

    # =========================
    # 🔥 3. TINCHLAR YUTISHI
    # =========================
    if peace > 0 and mafia == 0 and solo == 0:
        return "peace"

    # =========================
    # 🔥 4. Aralash holat — o‘yin davom etadi
    # =========================
    return None


async def stop_game_if_needed(game_id :int):
    game_id = int(game_id)
    game_state = games_state.get(int(game_id))
    if not game_state:
        return False

    winner_key = check_game_over(game_id)
    if not winner_key:
        return False

    game_state["meta"]["phase"] = "ended"
    game_state["meta"]["winner"] = winner_key

    chat_id = game_state.get("meta", {}).get("chat_id")

    final_text, winners, loosers = await build_final_game_text(game_id, winner_key)

    try:
        await send_safe_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode="HTML"
        )
    except Exception:
        pass

    game = Game.objects.filter(id=game_id).first()
    if game:
        game.is_active = False
        game.is_active_game = False
        game.is_ended = True
        game.save(update_fields=["is_active", "is_active_game", "is_ended"])

    all_players = game_state.get("players", [])
    roles_map = game_state.get("roles", {})

    users_qs = User.objects.filter(telegram_id__in=all_players)
    users_map = {u.telegram_id: u for u in users_qs}

    dm_payload = []

    

    with transaction.atomic():
        records = []

        for tg_id in all_players:
            u = users_map.get(int(tg_id))
            if not u:
                continue

            is_winner = u.telegram_id in winners

            records.append(
                MostActiveUser(
                    user=u,
                    group=int(chat_id),
                    games_played=1,
                    games_win=1 if is_winner else 0,
                )
            )

            if is_winner:
                u.coin += 55
                reward = 55
            else:
                u.coin += 25
                reward = 25

            u.save(update_fields=["coin"])

            role_key = roles_map.get(u.telegram_id)
            role_text = ROLE_LABELS.get(role_key, "Unknown")

            user_link = f"<a href='tg://user?id={u.telegram_id}'>{u.first_name}</a>"

            if is_winner:
                text = (
                    "O'yin tugadi!\n"
                    f"{role_text} rolida yutganingiz uchun sizga 💵 {reward} berildi!\n\n"
                    f"👤 {user_link}\n\n"
                    f"💵 Pullar: {u.coin}\n"
                    f"💎 Toshlar: {u.stones}\n\n"
                    f"🛡 Ximoya: {u.protection}\n"
                    f"📂 Hujjatlar: {u.docs}\n\n"
                )
            else:
                text = (
                    "O'yin tugadi!\n"
                    f"Siz {reward} 💶 qo'lga kiritdingiz.\n\n"
                    f"👤 {user_link}\n\n"
                    f"💵 Pullar: {u.coin}\n"
                    f"💎 Toshlar: {u.stones}\n\n"
                    f"🛡 Ximoya: {u.protection}\n"
                    f"📂 Hujjatlar: {u.docs}\n\n"
                )

            dm_payload.append((u.telegram_id, text))

        if records:
            MostActiveUser.objects.bulk_create(records)

    for user_id, text in dm_payload:
        try:
            await send_safe_message(
                chat_id=user_id,
                text=text,
                parse_mode="HTML",
                reply_markup=cart_inline_btn()
            )
        except Exception:
            pass

    games_state.pop(game_id, None)
    writing_allowed_groups.pop(chat_id, None)
    game_tasks.pop(game_id, None)

    game_settings = GameSettings.objects.first()
    if game_settings and game_settings.begin_after_end:
        from mafia_bot.handlers.command_handlers import auto_begin_game
        await auto_begin_game(chat_id)

    return True


def format_duration(seconds: int) -> str:
    m = seconds // 60
    s = seconds % 60
    return f"{m} min. {s} sek."

async def build_final_game_text(game_id: int, winner_key: str) -> str:
    game = games_state.get(game_id)
    if not game:
        return "O'yin tugadi."

    roles = game.get("roles", {})
    alive = set(game.get("alive", []))
    all_players = game.get("players", [])
    hanged = set(game.get("hanged", []))
    created_at = int(game.get("meta", {}).get("created_at", int(time.time())))
    duration = int(time.time()) - created_at

    winner_team_roles = (
        PEACE_ROLES if winner_key == "peace"
        else MAFIA_ROLES if winner_key == "mafia"
        else SOLO_ROLES if winner_key == "solo"
        else set()
    )

    winner_label = WINNER_LABEL.get(winner_key, winner_key)

    # players order bo'yicha ismni saqlab chiqarish uchun list ishlatamiz
    ids_in_order = [tg_id for tg_id in all_players if tg_id in roles]

    # userlarni 1 query bilan olamiz
    users_map = game.get("users_map", {})

    winners = []
    others = []
    winners_list = []
    loosers_list = []
    for tg_id in ids_in_order:
        role_key = roles.get(tg_id)
        user = users_map.get(tg_id)

        name = user.get("first_name") if user else str(tg_id)
        role_txt = role_label(role_key)

        line = f"    {name} - {role_txt}"

        # ✅ Winner bo'lish sharti: alive + winner team
        if tg_id in alive and role_key in winner_team_roles:
            winners.append(line)
            winners_list.append(tg_id)
        else:
            others.append(line)
            loosers_list.append(tg_id)
    suid_player = next((uid for uid, role in roles.items() if role == "suid"), None)

    if suid_player and suid_player in hanged:
        user = users_map.get(suid_player)
        name = user.get("first_name") if user else str(suid_player)
        role_txt = role_label("suid")

        line = f"    {name} - {role_txt}"

        if line not in winners:
            winners.append(line)
            winners_list.append(suid_player)

        if suid_player in loosers_list:
            loosers_list.remove(suid_player)
        

    text = (
        "O'yin tugadi!\n"
        f"G'olib: {winner_label}\n\n"
        "G'oliblar:\n"
    )

    if winners:
        text += "\n".join(winners)
    else:
        text += "    (yo'q)"

    text += "\n\nQolgan o'yinchilar:\n"

    if others:
        text += "\n".join(others)
    else:
        text += "    (yo'q)"

    text += f"\n\nO'yin: {format_duration(duration)} davom etdi"
    return text, winners_list, loosers_list

async def is_group_admin( chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False
    
    
async def mute_user(chat_id: int, user_id: int, seconds: int = 45):
    until_date = int(time.time()) + seconds

    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=ChatPermissions(
            can_send_messages=False,
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_voice_notes=False,
            can_send_polls=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        ),
        until_date=until_date
    )
    
    
def get_week_range(today):
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=7)
    return start, end


def get_month_range(today):
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


async def send_safe_message(chat_id: int, text: str, **kwargs) -> Message | None:
    try:
        return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
    except Exception:
        return None
    
    