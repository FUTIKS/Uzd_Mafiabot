import random
from decouple import config
from django.utils import timezone
from mafia_bot.utils import games_state
from aiogram.utils.keyboard import InlineKeyboardBuilder
from mafia_bot.models import Game, PriceStones,  PremiumGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from core.constants import ROLES_CHOICES,ROLE_PRICES_IN_MONEY,ROLE_PRICES_IN_STONES




def remove_prefix(text):
    return text.lstrip('@')

# Cart inline button

def group_profile_inline_btn(has_stone, chat_id):
    keyboard4 = InlineKeyboardButton(text="💎 Olmosni premiumga o'tkazish", url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start=stone_{chat_id}")
    keyboard1 = InlineKeyboardButton(text="⭐ evaziga 💎 sotib olish", callback_data="star_group")
    keyboard2 = InlineKeyboardButton(text="💳 Kartadan 💳 kartaga", url="https://t.me/RedDon_Mafia")
    keyboard3 = InlineKeyboardButton(text=" 🛠 O'yin boshqarish", url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start=instance_{chat_id}")
    keyboard5 = InlineKeyboardButton(text="✖️ Yopish", callback_data="close")
    keyboard = [keyboard4] if  has_stone else []
    design = [
        keyboard,
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard5],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def start_inline_btn():
    keyboard1 = InlineKeyboardButton(text= "ℹ️ Rollar haqida ma'lumot",url="https://t.me/MafiaRedDon_Roles/39")
    keyboard2 = InlineKeyboardButton(text="☑️ Botni guruhga qo'shish haqida ma'lumot",url="https://t.me/MafiaRedDon_Roles/96")
    keyboard3 = InlineKeyboardButton(text="➕ Botni guruhga qo'shish", url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?startgroup=true")
    keyboard4 = InlineKeyboardButton(text="⭐ Premium guruhlar", callback_data="groups")
    keyboard5 = InlineKeyboardButton(text="👤 Profil", callback_data="profile")
    keyboard6 = InlineKeyboardButton(text="🎭 Rollar", callback_data="role_menu")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard4],
        [keyboard5],
        [keyboard6],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def take_stone_btn():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="💎 Olmosni olish", callback_data="take_stone"))
    return kb.as_markup()

def take_gsend_stone_btn():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="💎 Olmosni olish", callback_data="take_gsend_stone"))
    return kb.as_markup()

def giveaway_join_btn():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="✅ Giveawayga qo‘shilish", callback_data="giveaway_join"))
    return kb.as_markup()

def admin_inline_btn():
    keyboard1 = InlineKeyboardButton(text=" 💬 Guruhlar obunasi", callback_data="trial")
    keyboard2 = InlineKeyboardButton(text=" ⭐ Premium guruhlar", callback_data="premium_group")
    keyboard3 = InlineKeyboardButton(text=" 👥 Foydalanuvchi bilan aloqa", callback_data="user_talk")
    keyboard4 = InlineKeyboardButton(text=" 📢 Botga habar jo'natish", callback_data="broadcast_message")
    keyboard5 = InlineKeyboardButton(text=" 📊 Statistika", callback_data="statistics")
    keyboard6 = InlineKeyboardButton(text=" 💶 Pul jo'natish", callback_data="send_pul")
    keyboard7 = InlineKeyboardButton(text=" 💎 Olmos jo'natish",callback_data="send_olmos")
    keyboard8 = InlineKeyboardButton(text=" 💶 Pul yechib olish", callback_data="remove_pul")
    keyboard9 = InlineKeyboardButton(text=" 💎 Olmos yechib olish",callback_data="remove_olmos")
    keyboard10 = InlineKeyboardButton(text=" 💰 Pul narxini o'zgartirish",callback_data="change_money")
    keyboard11 = InlineKeyboardButton(text=" 💎 Olmos narxini o'zgartirish",callback_data="change_stone")
    keyboard12 = InlineKeyboardButton(text=" 💳 O'tkazmalar tarixi",callback_data="transfer_history")
    keyboard13 = InlineKeyboardButton(text=" 🔒 Xavsizlik sozlamalari", callback_data="privacy")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard4],
        [keyboard5],
        [keyboard6,keyboard7],
        [keyboard8,keyboard9],
        [keyboard10],
        [keyboard11],
        [keyboard12],
        [keyboard13],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def main_keyboard(uuid) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Javob berish", url=f"https://t.me/{config('BOT_USERNAME')}?start={uuid}"),
        ],
    ])
    return keyboard

def answer_admin(tg_id,msg_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✍️ Javob berish", callback_data=f"answer_admin_{tg_id}_{msg_id}"),
        ],
    ])
    return keyboard

def end_talk_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🛑 Suhbatni yakunlash", callback_data="end_talk"),
        ],
    ])
    return keyboard

def back_btn(place="profile"):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back_{place}")]
        ]
    )
    return keyboard

def back_admin_btn():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")]
        ]
    )
    return keyboard

def case_inline_btn():
    keyboard1 = InlineKeyboardButton(text="💰 Pulli sandiq", callback_data="case_money")
    keyboard2 = InlineKeyboardButton(text="💎 Olmosli sandiq", callback_data="case_stone")
    keyboard3 = InlineKeyboardButton(text="⭐ Vip foydalanuvchi", callback_data="case_vip")
    keyboard4 = InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_profile")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard4],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def cart_inline_btn():
    keyboard1 = InlineKeyboardButton(text="🛒 Do'kon", callback_data="cart")
    keyboard2 = InlineKeyboardButton(text="💶 Sotib olish", callback_data="money_money")
    keyboard3 = InlineKeyboardButton(text="💎 Sotib olish", callback_data="money_stone")
    keyboard6 = InlineKeyboardButton(text="🥷 Mening Geroyim", callback_data="geroy_no_0")
    keyboard4 = InlineKeyboardButton(text="⭐ Premium guruhlar", callback_data="groups")
    keyboard5 = InlineKeyboardButton(text="📦  Sandiqlar", callback_data="cases")
    design = [
        [keyboard1],
        [keyboard2,keyboard3],
        [keyboard6],
        [keyboard4],
        [keyboard5],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

# Shop inline button
def shop_inline_btn():
    keyboard1 = InlineKeyboardButton(text="🛡 Ximoya - 250 💵", callback_data="buy_protection_0")
    keyboard2 = InlineKeyboardButton(text="📂 Hujjatlar - 500 💵", callback_data="buy_docs_0")
    keyboard3 = InlineKeyboardButton(text="🎗️ Osilishdan ximoya  - 20000 💵", callback_data="buy_hangprotect_1")
    keyboard4 = InlineKeyboardButton(text="🎗️ Osilishdan ximoya  - 20 💎", callback_data="buy_hangprotect_2")
    keyboard5 = InlineKeyboardButton(text="🎭 Rol sotib olish", callback_data="buy_activerole_0")
    keyboard6 = InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_profile")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
        [keyboard4],
        [keyboard5],
        [keyboard6],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def get_role_price(role_key: str):
    if role_key in ROLE_PRICES_IN_STONES:
        return "💎", ROLE_PRICES_IN_STONES[role_key]
    if role_key in ROLE_PRICES_IN_MONEY:
        return "💵", ROLE_PRICES_IN_MONEY[role_key]
    return "", 0

def role_shop_inline_keyboard():
    builder = InlineKeyboardBuilder()
    roles = ROLES_CHOICES[:-2]

    for role_key, role_name in roles:
        cur, price = get_role_price(role_key)

        builder.add(
            InlineKeyboardButton(
                text=f"{role_name} - {cur} {price}",
                callback_data=f"active_{role_key}_{price}",
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_profile"
        )
    )

    builder.adjust(2, 2, 2, 2, 2, 2, 2, 2, 2, 1)
    return builder.as_markup()

def pay_for_money_inline_btn(is_money):
    builder = InlineKeyboardBuilder()
    if is_money:
        callback1 = "p2p_money"
        callback2 = "star_money"
    else:
        callback1 = "p2p_stone"
        callback2 = "star_stone"
    builder.add(
        InlineKeyboardButton(
            text="💳 Kartadan 💳 kartaga",
            callback_data=callback1
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="⭐ Telegram yulduzlar evaziga",
            callback_data=callback2
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_profile"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

import json
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

MONEY_FOR_STAR = {
    1000: 7,
    10000: 77,
    50000: 340,
    100000: 680,
}

STONE_FOR_STAR = {
    1: 7,
    10: 68,
    30: 185,
    50: 237,
    70: 382,
    100: 513,
}


def pay_using_stars_inline_btn(is_money: bool):
    builder = InlineKeyboardBuilder()

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    money_map = json.loads(cost.money_in_star or "{}")
    stone_map = json.loads(cost.stone_in_star or "{}")

    if is_money:
        for money_amount, star_amount in money_map.items():
            builder.add(
                InlineKeyboardButton(
                    text=f"💶 {money_amount} - ⭐ {star_amount}",
                    callback_data=f"pul_{money_amount}_{star_amount}"
                )
            )
    else:
        for stone_amount, star_amount in stone_map.items():
            builder.add(
                InlineKeyboardButton(
                    text=f"💎 {stone_amount} - ⭐ {star_amount}",
                    callback_data=f"olmos_{stone_amount}_{star_amount}"
                )
            )

    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_profile"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


# Roles inline button
def roles_inline_btn():
    builder = InlineKeyboardBuilder()
    
    for role in ROLES_CHOICES:
        button = InlineKeyboardButton(text=role[1], callback_data=f"roles_{role[0]}")
        builder.add(button)
    builder.adjust(2)
    keyboard = builder.as_markup()
    return keyboard   
        
# Join game button
def join_game_btn(uuid):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🤵🏻 Qo'shilish",
                url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}?start={uuid}"  # game.code yoki game.uuid
            )]
        ]
    )
    return keyboard
# Go to bot inline button
def go_to_bot_inline_btn(number=1):
    if number == 1:
        text = "🤵🏻 Rolni ko'rish"
    elif number == 2:
        text = "🤵🏻 Botga o'tish"
    elif number == 3:
        text = "🗳 Ovoz berish"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=text,
                url=f"https://t.me/{remove_prefix(config('BOT_USERNAME'))}"  
            )]
        ]
    )
    return keyboard

# Doctor inline button
def doc_btn(players,doctor_id=None,game_id=None,chat_id=None,day=None):
    builder = InlineKeyboardBuilder()
    game = games_state.get(int(game_id), {})
    used_self = game.get("limits", {}).get("doc_self_heal_used", set())
    for player in players :
        first_name = player.get("first_name")
        tg_id = player.get("tg_id")
        if tg_id == doctor_id and doctor_id in used_self:
            continue
        callback=f"doc_{tg_id}_{game_id}_{chat_id}_{day}"
    
        button = InlineKeyboardButton(
            text=first_name,
            callback_data=callback
        )
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech kimni davolamaslik",
            callback_data=f"doc_no_{game_id}_{chat_id}_{day}"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


# Commander inline button
def com_inline_btn(game_id,chat_id,day=None):
    builder = InlineKeyboardBuilder()
    button1 = InlineKeyboardButton(text="🔫 O'q uzish", callback_data=f"com_shoot_{game_id}_{chat_id}_{day}")
    button2 = InlineKeyboardButton(text="🔍 Tekshirish", callback_data=f"com_protect_{game_id}_{chat_id}_{day}")
    builder.add(button1)
    builder.add(button2)
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech narsa qilmaslik",
            callback_data=f"com_no_{game_id}_{chat_id}_{day}"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

# Com inline action button
def com_inline_action_btn(action,game_id,chat_id,day=None,com_id=None):
    builder = InlineKeyboardBuilder()
    game = games_state.get(int(game_id), {})
    alive_players = game.get("alive", [])
    users_map = game.get("users_map", {})
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    alive_users_qs = [users_map[tg_id] for tg_id in alive_players if tg_id in users_map]
    
    for user in alive_users_qs:
        tg_id = user.get("tg_id")
        first_name = user.get("first_name")
        role = roles_map.get(tg_id)
        
        if role == "elf":
            text= f"🧝🏻‍♂ {first_name}"
        else:
            text= first_name
        if user.get("tg_id") == com_id:
            continue
        
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"{action}_{tg_id}_{game_id}_{day}"
        )
        
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="🔙",
            callback_data=f"com_back_{game_id}_{chat_id}_{day}"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

# Kamikaze inline button

def elf_inline_btn(players, elf_id, game_id, chat_id, day=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    
    for user in players:
        tg_id = user.get("tg_id")
        first_name = user.get("first_name")
        role = roles_map.get(tg_id)
        
        if role == "doc":
            text= f"👩‍⚕️ {first_name}"
        elif role == 'peace':
            text= f"🧑🏻 {first_name}"
        else:
            text= first_name
            
        if user.get("tg_id") == elf_id:
            continue
        
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"elf_{tg_id}_{game_id}_{chat_id}_{day}"
        )
        
        builder.add(button)
    builder.adjust(1)
    return builder.as_markup()




def action_inline_btn(action,own_id,players,game_id,chat_id,day=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)
        if not role == "rage" and tg_id == own_id:
            continue
        text = first_name 
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"{action}_{tg_id}_{game_id}_{chat_id}_{day}"
        )
        builder.add(button)
    
    button = InlineKeyboardButton(
        text="🚷 Hech nima qilmaslik",
        callback_data=f"{action}_no_{game_id}_{chat_id}_{day}"
    )
    builder.add(button)

    builder.adjust(1)
    return builder.as_markup()

def confirm_hang_inline_btn(voted_user_id,game_id,chat_id,yes=0, no=0):
    builder = InlineKeyboardBuilder()
    button_yes = InlineKeyboardButton(
        text=f"👍 {yes}",
        callback_data=f"con_yes_{voted_user_id}_{game_id}_{chat_id}"
    )
    button_no = InlineKeyboardButton(
        text=f"👎 {no}",
        callback_data=f"con_no_{voted_user_id}_{game_id}_{chat_id}"
    )
    builder.add(button_yes)
    builder.add(button_no)
    builder.adjust(2)
    return builder.as_markup()


    


def don_inline_btn(players,  game_id, chat_id, don_id,day=None):
    builder = InlineKeyboardBuilder()

    roles_map = games_state.get(int(game_id), {}).get("roles", {})

    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)

        if tg_id == don_id:
            continue
        
        if role == "mafia":
            continue
        elif role == "spy":
            text = f"🦇 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name

        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"don_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech kimni oldirmaslik",
            callback_data=f"don_no_{game_id}_{chat_id}_{day}"
    ))

    builder.adjust(1)
    return builder.as_markup()


def mafia_inline_btn(players, game_id,day=None):
    builder = InlineKeyboardBuilder()

    roles_map = games_state.get(int(game_id), {}).get("roles", {})

    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)

        
        
        if role == "mafia":
            continue
        elif role == "don":
            continue
        elif role == "spy":
            text = f"🦇 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name

        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"mafia_{tg_id}_{game_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech kimni oldirmaslik",
            callback_data=f"mafia_no_{game_id}_{day}"
    ))
    builder.adjust(1)
    return builder.as_markup()


def adv_inline_btn(players,  game_id, chat_id,day=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)
        if role not in ["don", "mafia"]:
            continue
        if role == "don":
            text = f"🤵🏻 {first_name}"
        else:
            text = f"🤵🏼 {first_name}"
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"adv_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech kimni himoya qilmaslik",
            callback_data=f"adv_no_{game_id}_{chat_id}_{day}"
    ))

    builder.adjust(1)
    return builder.as_markup()


def spy_inline_btn(players,  game_id, chat_id,day=None,spy_id=None):
    builder = InlineKeyboardBuilder()
    roles_map = games_state.get(int(game_id), {}).get("roles", {})
    for player in players:
        tg_id = player.get("tg_id")
        first_name = player.get("first_name")
        role = roles_map.get(tg_id)
        
        if tg_id == spy_id:
            continue
        
        if role == "don":
            text = f"🤵🏻 {first_name}"
        elif role == "mafia":
            text = f"🤵🏼 {first_name}"
        elif role == "adv":
            text = f"👨🏻‍💻 {first_name}"
        else:
            text = first_name
        builder.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"spy_{tg_id}_{game_id}_{chat_id}_{day}"
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="🚷 Hech kimni tekshirmaslik",
            callback_data=f"spy_no_{game_id}_{chat_id}_{day}"
    ))
    builder.adjust(1)
    return builder.as_markup()

    
def hang_inline_btn(players, own_id, game_id, chat_id,day=None):
    builder = InlineKeyboardBuilder()

    for tg_id, first_name in players.values():
        if tg_id == own_id:
            continue
        text = first_name
        button = InlineKeyboardButton(
            text=text,
            callback_data=f"hang_{tg_id}_{game_id}_{chat_id}_{day}"
        )
        builder.add(button)

    builder.adjust(1)
    return builder.as_markup()


def groups_inline_btn():
    builder = InlineKeyboardBuilder()
    premium_groups = PremiumGroup.objects.all().order_by("-stones_for")
    for group in premium_groups:
        if group.link is None or group.name is None:
            continue
        if group.ends_date and group.ends_date < timezone.now():
            group.delete()
            continue
        if "@"  in group.link:
            url = f"https://t.me/{remove_prefix(group.link)}"
        elif "http" in group.link or "https" in group.link:
            url = group.link
        button = InlineKeyboardButton(
            text=f"{group.name} - {group.stones_for} 💎",
            url=url
        )
        builder.add(button)
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_profile"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def groupes_keyboard(questions, page: int, total: int, per_page: int, all=False) :
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"quiz_select:{q.id}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"quiz_page:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"quiz_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text="Guruh qo'shish ➕",
            callback_data="add_group"
        ),
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        ),
    )

    return builder.as_markup()

def trial_groupes_keyboard(questions, page: int, total: int, per_page: int, all=False) :
    builder = InlineKeyboardBuilder()
    start_index = (page - 1) * per_page

    for i, q in enumerate(questions, start=start_index + 1):
        builder.button(
            text=str(i),
            callback_data=f"olga_select:{q.id}"
        )

    builder.adjust(5)
    nav_buttons = []
    total_pages = (total + per_page - 1) // per_page

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"olga_page:{page - 1}"
            )
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"olga_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    # Orqaga tugmasi
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        ),
    )

    return builder.as_markup()

def group_manage_btn(quiz_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="📝 Tahrirlash",
            callback_data=f"manage_edit:{quiz_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="❌ O'chirish",
            callback_data=f"manage_delete:{quiz_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        )
    )
    builder.adjust(1)
    return builder.as_markup()

def change_money_cost():
    keyboard = InlineKeyboardButton(
        text="💳 Puldagi narxni o'zgartirish", callback_data="aziz_money")
    keyboard1 = InlineKeyboardButton(
        text="⭐ Starsdagi narxni o'zgartirish", callback_data="aziz_star")
    keyboard2 = InlineKeyboardButton(
        text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard],
        [keyboard1],
        [keyboard2],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard

def change_stones_cost():
    keyboard = InlineKeyboardButton(
        text="💳 Puldagi narxni o'zgartirish", callback_data="ozgar_money")
    keyboard1 = InlineKeyboardButton(
        text="⭐ Starsdagi narxni o'zgartirish", callback_data="ozgar_star")
    keyboard2 = InlineKeyboardButton(
        text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard],
        [keyboard1],
        [keyboard2],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard


def money_case():
    builder = InlineKeyboardBuilder()
    
    for i in range(0,10):
        number = random.randint(899,2000)
        button = InlineKeyboardButton(
            text=f"{i+1}",
            callback_data=f"open_money_{number}"
        )
        builder.add(button)
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_case"
        )
    )
    return builder.as_markup()
        
def stone_case():
    builder = InlineKeyboardBuilder()
    
    for i in range(0,10):
        number = random.randint(3,12)
        button = InlineKeyboardButton(
            text=f"{i+1}",
            callback_data=f"open_stone_{number}"
        )
        builder.add(button)
    builder.adjust(5)
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_case"
        )
    )
    return builder.as_markup()

def begin_instance_inline_btn(chat_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔢 O'yinchilar to'lganda boshlash",
                callback_data=f"begin_instance_{chat_id}"
            )],
            [InlineKeyboardButton(
                text="⏱ Belgilangan vaqtdan so'ng boshlash",
            callback_data=f"begin_time_{chat_id}"
            )],
            [
                InlineKeyboardButton(
                text="🔁 O'yin tugagach auto boshlash",
                callback_data=f"begin_auto_{chat_id}"
            )],
            [InlineKeyboardButton(
                text="⬅️ Orqaga",
                callback_data="back_profile"
            )]
        ]
    )
    return keyboard

def trial_group_manage_btn(group_id):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Obunani uzaytish 🔄",
            callback_data=f"extend:{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Guruh hisobiga coin qo'shish ➕",
            callback_data=f"add_pul_{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="Guruh hisobiga olmos qo'shish ➕",
            callback_data=f"add_stone_{group_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_groups"
        )
    )
    builder.adjust(1)
    return builder.as_markup()



def history_groupes_keyboard(page: int, total: int, per_page: int):
    builder = InlineKeyboardBuilder()

    total_pages = (total + per_page - 1) // per_page

    nav_buttons = []

    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Oldingi",
                callback_data=f"history_page:{page - 1}"
            )
        )

    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ➡️",
                callback_data=f"history_page:{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_admin"
        )
    )

    return builder.as_markup()

def groups_buy_stars(chat_id):
    builder = InlineKeyboardBuilder()

    cost = PriceStones.objects.first()
    if not cost:
        cost = PriceStones.objects.create()

    stone_map = json.loads(cost.stone_in_star or "{}")

    for stone_amount, star_amount in stone_map.items():
        builder.add(
            InlineKeyboardButton(
                text=f"💎 {stone_amount} - ⭐ {star_amount}",
                url=f"https://t.me/{remove_prefix(config("BOT_USERNAME"))}?start=paym_{chat_id}_{stone_amount}_{star_amount}"
            )
        )
    
    builder.add(
        InlineKeyboardButton(
            text="⬅️ Orqaga",
            callback_data="back_group"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def stones_to_premium_inline_btn(stones: int, chat_id: int):
    builder = InlineKeyboardBuilder()

    amounts = [20, 25, 30, 50, 100, 150, 200, 300]

    for amount in amounts:
        if stones >= amount:
            builder.add(
                InlineKeyboardButton(
                    text=f"⭐ Premium ({amount} 💎)",
                    callback_data=f"prem_{amount}_{chat_id}"
                )
            )

    builder.add(
        InlineKeyboardButton(
            text="✖️ Yopish",
            callback_data="close"
        )
    )

    builder.adjust(1)
    return builder.as_markup()


def privacy_inline_btn():
    keyboard1 = InlineKeyboardButton(text=" 🔑 Parolni o'zgartirish", callback_data="credentials_password")
    keyboard2 = InlineKeyboardButton(text=" 👤 Username o'zgartirish", callback_data="credentials_username")
    keyboard3 = InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard3],
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=design)
    return keyboard


def use_hero_inline_btn(game_id, chat_id, day=None):
    builder = InlineKeyboardBuilder()        
    
    builder.add(InlineKeyboardButton(
                text="🥷 Hujum qilish",
                callback_data=f"hero_attack_{game_id}_{chat_id}_{day}"
            ))
    builder.add(InlineKeyboardButton(
                text="🛡 Himoyalanish",
                callback_data=f"hero_protect_{game_id}_{chat_id}_{day}"
            ))
    builder.adjust(1)
    return builder.as_markup()


def geroy_inline_btn(is_geroy):
    keyboard1 = InlineKeyboardButton(text="🥷 Sotib olish 💎 50", callback_data="geroy_buy_50")
    keyboard2 = InlineKeyboardButton(text="🥷 Sotib olish 💵 50000", callback_data="geroy_buy_50000")
    keyboard3 = InlineKeyboardButton(text="✖️ Geroyni olib tashlash", callback_data="geroy_sold_0")
    keyboard4 = InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_profile")
    design = [
        [keyboard1],
        [keyboard2],
        [keyboard4],
    ]
    if is_geroy:
        design = [
            [keyboard3],
            [keyboard4],
        ]
    return InlineKeyboardMarkup(inline_keyboard=design)