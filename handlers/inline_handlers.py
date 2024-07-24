from telethon import events, Button
from telethon.tl.types import InputWebDocument, UpdateBotInlineSend

from utils.data_management import load_user_data, save_user_data
from utils.external_services import get_ton_usd_price, generate_cheque_id

from bot import client
from config import *

@client.on(events.InlineQuery)
async def inline_send(event):
    query = event.text
    if query.startswith('t_'):
        cheque_id = query
        user_id = event.sender_id
        user_data = load_user_data(user_id)

        cheque = None
        for c in user_data["cheques"]:
            if c["id"] == f"{cheque_id}":
                cheque = c
                break

        if cheque is None:
            return

        amount = float(cheque["amount"])
        amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
        currency = cheque["currency"]
        tied_to_user = cheque.get("tied_to_user")
        comment = cheque.get("comment")

        ton_price = amount * get_ton_usd_price() if currency == 'TON' else amount

        title = f"Чек на {amount_str} {currency} ({ton_price:.2f}$)"
        description = f"Нажмите для отправки {amount_str} {currency}"
        if tied_to_user:
            description += f" для {tied_to_user['name']}"

        user_info = f' для <b><a href="tg://user?id={tied_to_user["id"]}">{tied_to_user["name"]}</a></b>' if tied_to_user else ''
        comment_text = f'\n\n💬 {comment}' if comment else ''

        result = event.builder.article(
            title=title,
            description=description,
            text=f"🚀 <b>Чек</b> на <b>{amount_str} {currency} ({ton_price:.2f}$)</b>{user_info}{comment_text}",
            thumb=InputWebDocument(
                url="https://i.imgur.com/m0SU0WN.png",
                size=0,
                mime_type="image/png",
                attributes=[]
            ),
            parse_mode="HTML",
            buttons=[Button.url(f'Получить {amount_str} {currency}', f'https://t.me/{bot_username}?start={cheque_id}')]
        )

        await event.answer([result], cache_time=1)

@client.on(events.InlineQuery)
async def create_cheque_inline(event):
    query = event.text
    if query != "" and not query.startswith("t_"):
        parts = query.split()
        amount = float(parts[0])
        currency = None
        username = None
        comment = None

        if len(parts) > 1 and parts[1].lower() in ['usdt', 'ton']:
            currency = parts[1].lower()
            username = parts[2] if len(parts) > 2 and parts[2].startswith('@') else None
            comment = ' '.join(parts[3:]) if len(parts) > 3 and username else None
        else:
            username = parts[1] if len(parts) > 1 and parts[1].startswith('@') else None
            if username:
                comment = ' '.join(parts[2:]) if len(parts) > 2 else None
            else:
                comment = ' '.join(parts[1:]) if len(parts) > 1 else None

        amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
        user_id = event.sender_id
        user_data = load_user_data(user_id)

        balance_usdt = user_data["balance_usdt"]
        balance_usdt_str = f'{balance_usdt:.2f}'.rstrip('0').rstrip('.')
        balance_ton = user_data["balance_ton"]
        balance_ton_str = f'{balance_ton:.2f}'.rstrip('0').rstrip('.')
        ton_usd_price = get_ton_usd_price()

        results = []

        if (currency in ['usdt', None]) and balance_usdt >= amount:
            cheque_id = generate_cheque_id()
            article_id = f'USDT!{amount_str}!{cheque_id}'
            if username:
                article_id += f'!{username[1:]}'
            if comment and username:
                article_id += '!comment'

            description = f'Доступно {balance_usdt_str} USDT'
            if username:
                description += f' для {username}'
            if comment and username:
                description += f' · {comment}'

            text = f'🚀 <b>Чек</b> на <b>{amount_str} USDT ({amount_str}$)</b>'
            if username:
                text += f' для {username}'
            if comment and username:
                text += f'\n\n💬 {comment}'

            results.append(event.builder.article(
                id=article_id,
                title=f'Чек на {amount_str} USDT ({amount_str}$)',
                description=description,
                text=text,
                thumb=InputWebDocument(
                    url="https://i.imgur.com/m0SU0WN.png",
                    size=0,
                    mime_type="image/png",
                    attributes=[]
                ),
                parse_mode="HTML",
                buttons=[
                    [Button.url(f'Получить {amount_str} USDT', f'https://t.me/{bot_username}?start={cheque_id}')]
                ]
            ))

        if (currency in ['ton', None]) and balance_ton >= amount:
            amount_in_usd = amount * ton_usd_price
            cheque_id = generate_cheque_id()
            article_id = f'TON!{amount_str}!{cheque_id}'
            if username:
                article_id += f'!{username[1:]}'
            if comment and username:
                article_id += '!comment'

            description = f'Доступно {balance_ton_str} TON'
            if username:
                description += f' для {username}'
            if comment and username:
                description += f' · {comment}'

            text = f'🚀 <b>Чек</b> на <b>{amount_str} TON ({amount_in_usd:.2f}$)</b>'
            if username:
                text += f' для {username}'
            if comment and username:
                text += f'\n\n💬 {comment}'

            results.append(event.builder.article(
                id=article_id,
                title=f'Чек на {amount_str} TON ({amount_in_usd:.2f}$)',
                description=description,
                text=text,
                thumb=InputWebDocument(
                    url="https://i.imgur.com/m0SU0WN.png",
                    size=0,
                    mime_type="image/png",
                    attributes=[]
                ),
                parse_mode="HTML",
                buttons=[
                    [Button.url(f'Получить {amount_str} TON', f'https://t.me/{bot_username}?start={cheque_id}')]
                ]
            ))

        if results:
            await event.answer(results)

        if comment and username:
            user_data['adding_comment_inline'] = {
                'status': True,
                'comment': comment
            }
            save_user_data(user_id, user_data)

@client.on(events.Raw(UpdateBotInlineSend))
async def hz(event):
    user_id = event.user_id
    cheque_data = event.id

    info = cheque_data.split('!')
    if len(info) < 3:
        return

    currency = info[0]
    amount = float(info[1])
    amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
    cheque_id = info[2]

    username = info[3] if len(info) > 3 else None
    comment = None

    if 'comment' in cheque_data:
        user_data = load_user_data(user_id)
        if 'adding_comment_inline' in user_data and user_data['adding_comment_inline']['status']:
            comment = user_data['adding_comment_inline']['comment']

    user_data = load_user_data(user_id)
    cheque = {
        "id": cheque_id,
        "type": "personal",
        "amount": amount,
        "currency": currency,
        "status": "created"
    }
    if username:
        try:
            tied_user = await client.get_entity(username)
            cheque['tied_to_user'] = {
                'id': tied_user.id,
                'name': tied_user.first_name
            }
        except ValueError:
            pass
    if comment:
        cheque['comment'] = comment

    user_data["cheques"].append(cheque)
    user_data[f"balance_{currency.lower()}"] -= amount
    user_data['adding_comment_inline']['status'] = False
    user_data['adding_comment_inline']['comment'] = None
    save_user_data(user_id, user_data)

    if all_logs:
        log_message = f"[log] Пользователь {user_data['first_name']} (ID: {user_id}) создал чек на {amount_str} {currency}, ID чека: {cheque_id}"
        if username:
            log_message += f", для пользователя @{username}"
        if comment:
            log_message += f", с комментарием: {comment}"
        print(log_message)