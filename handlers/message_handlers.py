from telethon import events, types, Button

from utils.data_management import create_new_user, load_user_data, save_user_data
from utils.external_services import get_ton_usd_price, generate_cheque_id, format_balance

import json
from datetime import datetime
import os

from bot import client, start_time
from config import *

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    user = await client.get_entity(user_id)
    first_name = user.first_name
    last_name = user.last_name
    username = user.username

    user_data = load_user_data(user_id)
    if not user_data:
        user_data = create_new_user(user_id, first_name, last_name, username)

    user_data["creating_cheque"] = False
    user_data['locking_cheque'] = None
    user_data['adding_comment'] = None
    save_user_data(user_id, user_data)

    ton_usd_price = get_ton_usd_price()
    balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price
    balance_usdt = user_data["balance_usdt"]
    total_balance = balance_ton_price_in_usd + balance_usdt
    cheque_count = len([cheque for cheque in user_data["cheques"] if cheque["status"] == "created"])

    text = (f"🚀 <b>xRocket</b> — это бот-кошелёк для получения, отправки, покупки и хранения криптовалюты в Telegram.\n\n"
            f"О всех возможностях читайте в <a href='https://t.me/xrocketnewsru'>официальном канале</a>")

    buttons = [
        [
            Button.inline(f'💵 Мой кошелек ({total_balance:.2f}$)', b'Wallet'),
        ],
        [
            types.KeyboardButtonWebView(
                "💱 Web-биржа",
                "https://web.ton-rocket.com/",
        )
        ],
        [
            Button.inline(f'🏷 Чеки' + (f' · {cheque_count}' if cheque_count > 0 else ''), b'Cheques'),
            Button.inline('🗳 P2P Маркет', b'P2P'),
        ],
        [
            Button.inline('💱 Биржа', b'ExchangeV2'),
            Button.inline('📋 Счета', b'Invoices'),
        ],
        [
            Button.inline('💼 Сделки', b'Swaps'),
            Button.inline('🌟 Подписки', b'Subscriptions'),
        ],
        [
            Button.inline('🤖 Rocket Pay', b'RocketPay'),
            Button.inline('⚙️ Настройки', b'Settings'),
        ],
    ]
    if event.message.text == "/start":
        await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/market'))
async def market(event):
    text = (f'🗳 <b>Маркет</b>\n\n'
            f'Покупайте и продавайте <b>криптовалюту безопасно</b>, создавая объявления или откликаясь на объявления других пользователей.\n\n'
            f'Бот выступает <b>гарантом в сделке</b>, <b>блокируя криптовалюту</b> во время совершения сделки.\n\n'
            f'Текущая валюта маркета - <b>UAH</b>, изменить можно в <b>настройках маркета</b>.\n\n'
            f'Комиссия на покупку - <b>0%</b>, на продажу - <b>1%</b>\n\n'
            f'Если Вы нашли <b>ошибку</b> или у Вас есть запрос на <b>размещение новых валют или способов оплаты</b>, обращайтесь в <a href="https://t.me/{support_bot_username}"><b>тех. поддержку</b></a>.')

    buttons=[
                [
                    Button.inline('Купить', b'Buy'),
                    Button.inline('Продать', b'Sell'),
                ],
                [
                    Button.inline('❇️ Создать объявление', b'Create'),
                ],
                [
                    Button.inline('Мои сделки', b'ActiveUserDeals'),
                ],
                [
                    Button.inline('⚙️ Настройки маркета', b'P2P_Settings'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/wallet'))
async def wallet(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    ton_usd_price = get_ton_usd_price()
    balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price
    balance_ton = f'{user_data["balance_ton"]:f}'.rstrip('0').rstrip('.')
    balance_usdt = f'{user_data["balance_usdt"]:f}'.rstrip('0').rstrip('.')
    total_balance = balance_ton_price_in_usd + float(balance_usdt)

    text = (f'💵 <b>Ваш баланс</b>\n\n'
            f'<a href="https://ton.org/"><b>TON</b></a>: {balance_ton} TON ({balance_ton_price_in_usd:.2f}$)\n\n'
            f'<a href="https://tether.to/"><b>USDT</b></a>: {balance_usdt} USDT ({balance_usdt}$)\n\n'
            f'<b>≈ {total_balance:.2f}$</b>')
    buttons = [
        [
            Button.inline('📥 Пополнение', b'Deposit'),
            Button.inline('📤 Вывод', b'Withdraw'),
        ],
        [
            types.KeyboardButtonSwitchInline(
                '🏷 Отправить в сообщении', 
                f'')
        ],
        [
            Button.inline('🖼 NFT', b'NFT'),
        ],
        [
            Button.inline('‹ Назад', b'Back'),
        ],
    ]
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/exchange'))
async def exchange(event):
    text = (f"💱 <b>Биржа</b>\n\n"
            f"Торгуйте любой криптовалютой, которая есть в боте, как на обычной бирже.\n\n"
            f"Комиссия составляет <b>0.1%</b> для мейкеров и <b>0.15%</b> для тейкеров <b>с получаемой</b> суммы ордера.")

    buttons=[
                [
                    types.KeyboardButtonWebView(
                        "💱 Web-биржа",
                        "https://web.ton-rocket.com/",
                )
                ],
                [
                    Button.inline('Бот-биржа', b'BotExchange'),
                ],
                [
                    Button.inline('🏆 Рейтинг', b'Rank'),
                    Button.inline('⚙️ Настройки', b'Settings_Exchange'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/settings'))
async def settings(event):
    text = (f"⚙️ <b>Настройки</b>\n\n"
            f"Ваш язык: <b>🇷🇺 Русский</b>\n"
            f"Валюта бота: <b>USD · $</b>")

    buttons=[
                [
                    Button.url('🆘 Поддержка', f'https://t.me/{support_bot_username}'),
                ],
                [
                    Button.inline('💲 Отображение балансов', b'HideBalances'),
                ],
                [
                    Button.inline('Управление токенами', b'HideCoins'),
                ],
                [
                    Button.inline('Язык бота', b'Language'),
                    Button.inline('Валюта бота', b'BotCurrency'),
                ],
                [
                    Button.inline('📄 История ваших действий', b'History'),
                ],
                [
                    Button.inline('🔌 Привязать кошелёк', b'LinkWallet'),
                ],
                [
                    Button.inline('🗃 Управление группами', b'GroupsManagement'),
                ],
                [
                    Button.inline('💥 Реферальная система', b'RefSystem'),
                ],
                [
                    Button.inline('☄️ Заявка на листинг токена', b'Listing'),
                ],
                [
                    Button.inline('🌅 Лимиты и комиссии', b'LimitsFees'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/cheques'))
async def cheques(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    user_data["creating_cheque"] = False
    save_user_data(user_id, user_data)

    text = (f"🏷 <b>Чеки</b>\n\n"
            f"<b>Чеки</b> позволяют отправлять криптовалюту прямо в сообщениях.\n\n"
            f"· <i>Персональный чек</i> - для отправки монет одному пользователю\n"
            f"· <i>Мульти-чек</i> - для отправки монет нескольким пользователям с возможностью добавить условие подписки\n"
            f"· <i>Rocket-чек</i> - улучшенный мульти-чек с наградой за распространение\n\n<b>Выберите тип чека:</b>")

    buttons = [
        [
            Button.inline('Персональный', b'Personal'),
            Button.inline('Мульти-чек', b'Multi'),
        ],
        [
            Button.inline('🚀 Rocket-чек', b'Rocket'),
        ],
        [
            Button.inline('🎁 Доска чеков', b'ChequeBoard'),
        ],
        [
            Button.inline('‹ Назад', b'Back'),
        ],
    ]

    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/invoices'))
async def invoices(event):
    text = (f"📋 <b>Счета</b>\n\n"
            f"<b>Можно создать:</b>\n"
            f"· одноразовый - <i>счёт, который можно оплатить один раз</i>\n"
            f"· мульти-счёт - <i>счёт, который смогут оплатить несколько раз</i>\n\n"
            f"Оплачивать счета можно через <b>xRocket</b>, либо напрямую по <b>блокчейн-адресу</b>.")

    buttons=[
                [
                    Button.inline('Одноразовый', b'Single'),
                    Button.inline('Мульти-счёт', b'Multi'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/subscriptions'))
async def subscriptions(event):
    text = (f"🌟 <b>Подписки</b>\n\n"
            f"Управляйте и создавайте подписки в этом разделе.\n\n"
            f"<b>Мои подписки</b> <i>- действующие подписки или те, которые Вы когда-либо оплачивали</i>\n"
            f"<b>Созданные</b> <i>- созданные Вами подписки</i>")

    buttons=[
                [
                    Button.inline('Мои подписки', b'My'),
                    Button.inline('Созданные', b'Created'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage(pattern='/rocketpay'))
async def rocketpay(event):
    text = (f"🤖 <b>Rocket Pay</b>\n\n"
            f"Интегрируйте платежное <b>API Rocket Pay</b> 🚀 в свой сервис.\n\n"
            f"<b>Вы можете создать чеки, счета и делать переводы, используя наше API.</b>\n\n"
            f"<i>Комиссия на входящие транзакции составит <b>1.5%</b>  (для счетов или пополнений приложений), все остальные операции <b>без комиссии.</b></i>")

    buttons=[
                [
                    Button.inline('Создать', b'Create'),
                ],
                [
                    Button.url('Документация Rocket Api', 'https://pay.ton-rocket.com/api/'),
                ],
                [
                    Button.url('Документация Exchange Api', 'https://trade.ton-rocket.com/api'),
                ],
                [
                    Button.inline('Чат для разработчиков АПИ', b'DevChat'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage)
async def amount(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    if user_data["creating_cheque"] == False:
        return

    last_message_id = user_data.get("last_message_id")
    try:
        amount = float(event.message.message)
        if amount <= 0:
            raise ValueError

        currency = user_data.get("creating_cheque_currency")
        if currency == "TON":
            if amount > user_data["balance_ton"]:
                ton_usd_price = get_ton_usd_price()
                balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price
                balance_ton_display = f"{user_data['balance_ton']:.2f}".rstrip('0').rstrip('.')
                balance_ton_price_display = f"{balance_ton_price_in_usd:.2f}".rstrip('0').rstrip('.')

                text = (f"🏷 <b>Персональный чек</b>\n\n"
                        f"Сколько TON Вы хотите отправить пользователю с помощью чека?\n\n"
                        f"<b>Максимум:</b> <b>{balance_ton_display} TON ({balance_ton_price_display}$)</b>\n"
                        f"Минимум: <b>0.00001 TON</b>\n\n"
                        f"<b>Введите сумму чека в TON:</b>\n\n"
                        f"🔺 <b>Недостаточно средств на балансе.</b>")

                buttons = [
                    [Button.inline(f'Максимум · {balance_ton_display} TON ({balance_ton_price_display}$)', b'Max_ton_personal')],
                    [Button.inline('‹ Выбор валюты', b'Create_Personal')],
                    [Button.inline('‹ Назад', b'Personal')],
                ]

                await event.message.delete()
                await client.edit_message(event.chat_id, last_message_id, text, buttons=buttons, parse_mode='html', link_preview=False)
                return

            cheque_id = generate_cheque_id()
            cheque = {
                "id": cheque_id,
                "type": "personal",
                "amount": amount,
                "currency": "TON",
                "status": "created"
            }
            cheque_ton_amount_price_in_usd = cheque["amount"] * get_ton_usd_price()
            cheque_amount_display = f"{cheque['amount']:.2f}".rstrip('0').rstrip('.')
            cheque_price_display = f"{cheque_ton_amount_price_in_usd:.2f}".rstrip('0').rstrip('.')

            text = (f"🏷 <b>Персональный чек</b>\n\n"
                    f"<b>Сумма чека</b>: {cheque_amount_display} TON ({cheque_price_display}$)\n\n"
                    f"<b>🔸 Пожалуйста, подтвердите корректность данных:</b>")

            buttons = [
                [Button.inline('✅ Подтверждаю', f'Success_create_ton_personal:{amount}'), Button.inline('❌ Отклоняю', b'Personal')],
                [Button.inline('‹ Изменить сумму', b'ton_personal')],
                [Button.inline('‹ Назад', b'Personal')]
            ]

        elif currency == "USDT":
            if amount > user_data["balance_usdt"]:
                balance_USDT_display = f"{user_data['balance_usdt']:.2f}".rstrip('0').rstrip('.')

                text = (f"🏷 <b>Персональный чек</b>\n\n"
                        f"Сколько USDT Вы хотите отправить пользователю с помощью чека?\n\n"
                        f"<b>Максимум:</b> <b>{balance_USDT_display} USDT ({balance_USDT_display}$)</b>\n"
                        f"Минимум: <b>0.00001 USDT</b>\n\n"
                        f"<b>Введите сумму чека в USDT:</b>\n\n"
                        f"🔺 <b>Недостаточно средств на балансе.</b>")

                buttons = [
                    [Button.inline(f'Максимум · {balance_USDT_display} USDT ({balance_USDT_display}$)', b'Max_usdt_personal')],
                    [Button.inline('‹ Выбор валюты', b'Create_Personal')],
                    [Button.inline('‹ Назад', b'Personal')],
                ]

                await event.message.delete()
                await client.edit_message(event.chat_id, last_message_id, text, buttons=buttons, parse_mode='html', link_preview=False)
                return

            cheque_id = generate_cheque_id()
            cheque = {
                "id": cheque_id,
                "type": "personal",
                "amount": amount,
                "currency": "USDT",
                "status": "created"
            }
            cheque_amount_display = f"{cheque['amount']:.2f}".rstrip('0').rstrip('.')

            text = (f"🏷 <b>Персональный чек</b>\n\n"
                    f"<b>Сумма чека</b>: {cheque_amount_display} USDT ({cheque_amount_display}$)\n\n"
                    f"<b>🔸 Пожалуйста, подтвердите корректность данных:</b>")

            buttons = [
                [Button.inline('✅ Подтверждаю', f'Success_create_usdt_personal:{amount}'), Button.inline('❌ Отклоняю', b'Personal')],
                [Button.inline('‹ Изменить сумму', b'usdt_personal')],
                [Button.inline('‹ Назад', b'Personal')]
            ]

        await event.message.delete()
        await client.edit_message(event.chat_id, last_message_id, text, buttons=buttons, parse_mode='html', link_preview=False)
    except ValueError:
        return
    
@client.on(events.NewMessage)
async def receive_comment(event):
    user_data = load_user_data(event.sender_id)
    if 'adding_comment' in user_data and user_data['adding_comment']:
        cheque_id = user_data['adding_comment']
        comment = event.raw_text
        if len(comment) > 1000:
            comment = comment[:1000]
        
        try:
            cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
        except StopIteration:
            cheque_id = f't_{cheque_id}'
            try:
                cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
            except StopIteration:
                await event.reply("Чек с указанным ID не найден.")
                return

        cheque['comment'] = comment
        user_data['adding_comment'] = None
        save_user_data(event.sender_id, user_data)

        await showkok(event, cheque_id)
        await event.message.delete()
        if all_logs:
            print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) добавил описание к чеку, текст описания: {cheque['comment']}, ID чека: {cheque_id}")
    
async def showkok(event, cheque_id):
    user_data = load_user_data(event.sender_id)
    cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
    amount = float(cheque["amount"])
    amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
    amount_in_usd = amount * get_ton_usd_price()

    comment = cheque.get('comment', '')
    last_message_id = user_data.get("last_message_id")

    tied_to_user = cheque.get('tied_to_user', '')
    text = (f"🏷 <b>Персональный чек\n\n"
            f"Сумма чека:</b> {amount_str} {cheque['currency']} ({amount_in_usd:.2f}$)\n\n")

    if tied_to_user:
        text += f"Только для <a href='tg://user?id={tied_to_user['id']}'><b>{tied_to_user['name']}</b></a>\n\n"

    if comment:
        text += f"💬 {comment}\n\n"

    text += (f"‼️ <b>Никогда не делайте скриншот и не передавайте ссылку на чек людям, которым вы не доверяете.</b> Делая это, вы передаете средства в этом чеке безвозмездно, без гарантий получить что-то взамен. Мошенники могут использовать это, чтобы получить ваши монеты\n\n"
             f"<b>Ссылка на чек:</b>\n<span class='tg-spoiler'>t.me/{bot_username}?start={cheque_id}</span>")

    buttons = [
        [
            types.KeyboardButtonSwitchInline('💸 Отправить', f'{cheque_id}')
        ],
        [
            Button.inline('Показать QR-код', f'Qr:{cheque_id}'),
        ],
    ]

    if comment:
        buttons.append([Button.inline('Убрать описание', f'rm_comment:{cheque_id}')])
    else:
        buttons.append([Button.inline('Добавить описание', f'Comment:{cheque_id}')])

    if tied_to_user:
        buttons.append([Button.inline('Отвязать от пользователя', f'Unlock:{cheque_id}')])
    else:
        buttons.append([Button.inline('Привязать к пользователю', f'Lock:{cheque_id}')])

    buttons.extend([
        [Button.inline('Удалить', f'Delete:{cheque_id}')],
        [Button.inline('‹ Назад', b'My_Personal_Cheques')],
    ])
    
    await client.edit_message(event.chat_id, last_message_id, text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.NewMessage)
async def receive_lock(event):
    user_input = event.raw_text
    user_data = load_user_data(event.sender_id)

    if 'locking_cheque' in user_data and user_data['locking_cheque']:
        cheque_id = user_data['locking_cheque']
        
        try:
            if event.message.forward:
                user_id = event.message.forward.from_id.user_id
                forwarded_user_data = load_user_data(user_id)
                user_name = forwarded_user_data['first_name'] if forwarded_user_data else None
            else:
                user = await client.get_entity(user_input)
                user_id = user.id
                user_name = user.first_name if user.first_name else None

            cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
            cheque['tied_to_user'] = {'id': user_id, 'name': user_name}
            user_data['locking_cheque'] = None
            save_user_data(event.sender_id, user_data)
            if all_logs:
                print(f"[log] Пользователь {user_data['first_name']} (ID: {user_id}) привязал чек к пользователю {cheque['tied_to_user']['name']} (ID: {cheque['tied_to_user']['id']}), ID чека: {cheque['id']}")

            await showkok(event, cheque_id)
            await event.message.delete()

        except AttributeError:
            last_message_id = user_data.get("last_message_id")
            text = ("🏷 <b>Персональный чек</b>\n\n"
                    f"Отправьте мне <b>@username</b> пользователя или перешлите любое сообщение от него.\n\n"
                    f"🔺 <b>Вы послали некорректное имя пользователя либо мы не можем распознать пользователя по пересланному сообщению из-за его настроек приватности.</b>")
            buttons = [
                        [Button.inline('‹ Назад', f'cheque_{cheque_id}')]
                    ]
            await client.edit_message(event.chat_id, last_message_id, text, buttons=buttons, parse_mode='html', link_preview=False)
            await event.message.delete()

        except Exception as e:
            await event.reply(f"Произошла ошибка: {str(e)}")

async def activate_cheque(event, cheque_id):
    user_id = event.sender_id
    recipient_user_data = load_user_data(user_id)

    all_users_files = [f for f in os.listdir('users') if f.endswith('.json')]
    cheque = None
    sender_user_data = None
    for file in all_users_files:
        with open(f'users/{file}', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for ch in data["cheques"]:
                if ch["id"] == cheque_id and ch["status"] == "created":
                    cheque = ch
                    sender_user_data = data
                    break
        if cheque:
            break

    if cheque:
        tied_to_user = cheque.get('tied_to_user', None)
        
        if tied_to_user:
            if tied_to_user['id'] != user_id:
                lol = [
                    [
                        Button.inline('‹ Назад', b'wallet_message'),
                    ],
                ]
                await event.respond("Вы <b>не можете активировать</b> данный перевод.", parse_mode='html', buttons=lol)
                return

        if cheque["status"] != "created":
            kek = [
                [
                    Button.inline('‹ Назад', b'Wallet'),
                ],
            ]
            await event.respond("Этот перевод <b>уже активирован.</b>", buttons=kek, parse_mode="html")
            return
    else:
        kek = [
            [
                Button.inline('‹ Назад', b'Wallet'),
            ],
        ]
        await event.respond("Этот перевод <b>не найден</b> или <b>уже активирован.</b>", buttons=kek, parse_mode="html")
        return

    cheque["status"] = "activated"
    recipient_user_data[f"balance_{cheque['currency'].lower()}"] += cheque["amount"]
    save_user_data(user_id, recipient_user_data)
    sender_user_data["cheques"] = [ch for ch in sender_user_data["cheques"] if ch["id"] != cheque_id]
    save_user_data(sender_user_data["id"], sender_user_data)

    recipient = await client.get_entity(user_id)
    recipient_name = recipient.first_name if recipient.last_name is None else f"{recipient.first_name} {recipient.last_name}"
    amount = f'{cheque["amount"]:f}'.rstrip('0').rstrip('.')

    sender_text = f'<a href="tg://user?id={user_id}"><b>{recipient_name}</b></a> активировал(а) ваш чек на <b>{amount} {cheque["currency"]} ({cheque["amount"] * get_ton_usd_price() if cheque["currency"] == "TON" else cheque["amount"]:.2f}$)</b>.'
    cheburek = [
        [
            Button.inline('‹ Кошелёк', b'wallet_message'),
        ],
    ]
    await client.send_message(sender_user_data["id"], sender_text, buttons=cheburek, parse_mode='html')
    if all_logs:
        print(f"[log] Пользователь {recipient_user_data['first_name']} (ID: {user_id}) активировал чек на {amount} {cheque['currency']}, ID чека: {cheque['id']}")

    koks = [
        [
            Button.inline('‹ Назад', b'wallet_message'),
        ],
    ]
    recipient_text = (
        f'💰 Вы успешно получили <b>{amount} '
        f'{cheque["currency"]} ({cheque["amount"] * get_ton_usd_price() if cheque["currency"] == "TON" else cheque["amount"]:.2f}$)</b>.'
    )
    comment = cheque.get('comment', '')
    if comment:
        recipient_text += f"\n\n💬 {comment}"

    await event.respond(recipient_text, buttons=koks, parse_mode='html')

@client.on(events.NewMessage(pattern='/add'))
async def add(event):
    user_id = event.sender_id
    message = event.message.message.lower().strip()

    parts = message.split()
    
    if len(parts) != 3:
        await event.respond("❌ <b>Неправильный формат команды.</b> <i>Используй /add [usdt|ton] [сумма]</i>", parse_mode="html")
        return

    currency = parts[1].upper()
    amount_str = parts[2]

    try:
        amount = float(amount_str)
    except ValueError:
        await event.respond("❌ <b>Сумма должна быть числом</b>", parse_mode="html")
        return

    if amount.is_integer():
        amount = int(amount)

    if currency not in ['USDT', 'TON']:
        await event.respond("❌ <b>Поддерживаются только USDT и TON</b>", parse_mode="html")
        return

    user_data = load_user_data(user_id)
    if currency == 'USDT':
        user_data['balance_usdt'] += amount
    elif currency == 'TON':
        user_data['balance_ton'] += amount
    save_user_data(user_id, user_data)

    buttons=[
                [
                    Button.inline('‹ Кошелёк', b'wallet_message'),
                ],
            ]

    if currency == 'TON':
        amount_in_usd = amount * get_ton_usd_price()
        await event.respond(f"💵 <b>Вы </b><a href='https://tonviewer.com/UQABGo8KCza3ea8DNHMnSWZmbRzW-05332eTdfvW-XDQEmnJ'><b>внесли</b></a> на счёт <b>{amount} {currency} ({amount_in_usd:.2f}$) (TON)</b>", buttons=buttons, parse_mode="html", link_preview=False)
        if all_logs:
            print(f"[log] Пользователь {user_data['first_name']} (ID: {user_id}) пополнил баланс на {amount} {currency}")
    elif currency == 'USDT':
        await event.respond(f"💵 <b>Вы </b><a href='https://tronscan.org/#/token20/TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'><b>внесли</b></a> на счёт <b>{amount} {currency} ({amount}$) (TRX-TRC20)</b>", buttons=buttons, parse_mode="html", link_preview=False)
        if all_logs:
            print(f"[log] Пользователь {user_data['first_name']} (ID: {user_id}) пополнил баланс на {amount} {currency}")

@client.on(events.NewMessage(pattern='/start (.+)'))
async def start_with_cheque(event):
    cheque_id = event.pattern_match.group(1)
    await activate_cheque(event, cheque_id)

@client.on(events.NewMessage(pattern='/admin'))
async def admin(event):
    if event.sender_id == admin_id:
        user_count = len(os.listdir('users'))
        cheque_count = sum(len(load_user_data(user_id)['cheques']) for user_id in [int(f.split('.')[0]) for f in os.listdir('users')])

        uptime = datetime.now() - start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} д")
        if hours > 0 or days > 0:
            uptime_parts.append(f"{hours} ч")
        if minutes > 0 or hours > 0 or days > 0:
            uptime_parts.append(f"{minutes} мин")
        uptime_parts.append(f"{seconds} сек")

        uptime_text = " ".join(uptime_parts)

        text = (f'👋 <b>Добро пожаловать!</b>\n\n'
                f'📊 <b>Мини-стата:</b>\n\n'
                f'👤 Всего пользователей: <code>{user_count}</code>\n'
                f'🧾 Всего чеков: <code>{cheque_count}</code>\n\n'
                f'⏳ Аптайм бота: <code>{uptime_text}</code>\n\n')

        buttons = [Button.inline('Сделать рассылку', b'newsletter')]

        await event.respond(text, buttons=buttons, parse_mode="html")

@client.on(events.NewMessage(pattern=f'/user (.+)'))
async def get_user(event):
    if event.sender_id != admin_id:
        return
    
    user_id = int(event.pattern_match.group(1))
    user_data = load_user_data(user_id)

    if user_data:
        user_json = json.dumps(user_data, ensure_ascii=False, indent=4)
        json_path = f'{user_id}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(user_json)
        
        description_parts = [
            f'👤 <b>Инфа об юзере</b> <code>{user_id}</code>:\n\n'
            f'🦋 Имя: <b><a href="tg://user?id={user_data["id"]}">{user_data["first_name"]}</a></b>' if user_data.get("first_name") else "",
            f'🦋 Юзернейм: @{user_data["username"]}' if user_data.get("username") else "",
            f'👛 Баланс TON: <code>{format_balance(user_data["balance_ton"])}</code>' if user_data.get("balance_ton") is not None else "",
            f'💰 Баланс USDT: <code>{format_balance(user_data["balance_usdt"])}</code>' if user_data.get("balance_usdt") is not None else ""
        ]

        cheque_parts = [f'<code>{cheque["id"]}</code>' for cheque in user_data["cheques"]]
        aloy = ", ".join(cheque_parts)

        description = "\n".join(filter(None, description_parts)) + "\n🧾 Чеки:\n" + aloy

        await client.send_file(event.chat_id, json_path, caption=description, parse_mode='html')
        os.remove(json_path)
    else:
        await event.respond('🤷‍♂️ <b>Пользователь не найден</b>', parse_mode='html')

@client.on(events.NewMessage(pattern=f'/cheque (.+)'))
async def get_cheque(event):
    if event.sender_id != admin_id:
        return
    
    cheque_id = event.pattern_match.group(1)
    cheque = None
    owner = None

    for filename in os.listdir('users'):
        user_id = int(filename.split('.')[0])
        user_data = load_user_data(user_id)
        for c in user_data['cheques']:
            if c['id'] == cheque_id:
                cheque = c
                owner = user_data
                break
        if cheque:
            break

    if cheque and owner:
        cheque_json = json.dumps(cheque, ensure_ascii=False, indent=4)
        json_path = f'{cheque_id}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(cheque_json)

        description_parts = [
            f'🧾 <b>Чек</b> <code>{cheque["id"]}</code><b>:</b>\n',
            f'👤 Владелец: <b><a href="tg://user?id={owner["id"]}">{owner["first_name"]}</a></b>',
            f'💲 Сумма: <code>{format_balance(cheque["amount"])}</code>',
            f'💱 Валюта: <code>{cheque["currency"]}</code>',
            f'🐳 Привязан к пользователю: <b><a href="tg://user?id={cheque["tied_to_user"]["id"]}">{cheque["tied_to_user"]["name"]}</a></b>' if cheque.get("tied_to_user") else "",
            f'💬 Описание чека: <i>{cheque["comment"]}</i>' if cheque.get("comment") else ""
        ]

        description = "\n".join(filter(None, description_parts))

        await client.send_file(event.chat_id, json_path, caption=description, parse_mode='html')
        os.remove(json_path)
    else:
        await event.respond('🤷‍♂️ <b>Чек не найден</b>')