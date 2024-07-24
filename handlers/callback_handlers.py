from telethon import events, types, Button

from datetime import datetime
import os

from utils.data_management import create_new_user, load_user_data, save_user_data
from utils.external_services import get_ton_usd_price, generate_cheque_id, send_newsletter

from handlers.message_handlers import showkok

from bot import client, start_time
from config import *

@client.on(events.CallbackQuery(data=b'Wallet'))
@client.on(events.CallbackQuery(data=b'wallet_message'))
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
    if event.data == b'Wallet':
        await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    elif event.data == b'wallet_message':
        await event.respond(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Deposit'))
async def deposit(event):
    text = (f"📥 <b>Пополнение</b>\n\n"
            f"<b>Выберите валюту для пополнения:</b>")

    buttons=[
                [
                    Button.inline('TON', b'Deposit_TON'),
                    Button.inline('USDT', b'Deposit_USDT'),
                ],
                [
                    Button.inline('TON Токены', b'CoinsList_TOKENS-1'),
                ],
                [
                    Button.inline('‹ Назад', b'Wallet'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Withdraw'))
async def withdraw(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    ton_usd_price = get_ton_usd_price()
    balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price
    balance_ton = f'{user_data["balance_ton"]:f}'.rstrip('0').rstrip('.')
    balance_usdt = f'{user_data["balance_usdt"]:f}'.rstrip('0').rstrip('.')

    text = (f"📥 <b>Вывод</b>\n\n<b>TON</b>: {balance_ton} TON ({balance_ton_price_in_usd:.2f}$)\n"
            f"<b>USDT</b>: {balance_usdt} USDT ({balance_usdt}$)\n\n"
            f"<a href='https://t.me/xrocket?start=fees_wallet-w'><i>Лимиты и комиссии</i></a>\n\n"
            f"<b>Выберите валюту которую хотите вывести:</b>")

    buttons=[
                [
                    Button.inline('TON', b'Withdraw_TON'),
                    Button.inline('USDT', b'Withdraw_USDT'),
                ],
                [
                    Button.inline('TON Токены', b'CoinsList_TOKENS-1'),
                ],
                [
                    Button.inline('‹ Назад', b'Wallet'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Back'))
async def back(event):
    user_id = event.sender_id
    user = await client.get_entity(user_id)
    first_name = user.first_name
    last_name = user.last_name
    username = user.username

    user_data = load_user_data(user_id)
    if not user_data:
        user_data = create_new_user(user_id, first_name, last_name, username)

    ton_usd_price = get_ton_usd_price()
    balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price
    balance_usdt = user_data["balance_usdt"]
    total_balance = balance_ton_price_in_usd + balance_usdt
    cheque_count = len([cheque for cheque in user_data["cheques"] if cheque["status"] == "created"])

    text = (f'🚀 <b>xRocket</b> — это бот-кошелёк для получения, отправки, покупки и хранения криптовалюты в Telegram.\n\n'
            f'О всех возможностях читайте в <a href="https://t.me/xrocketnewsru">официальном канале</a>')

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
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'P2P'))
async def p2p(event):
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'ExchangeV2'))
async def exchangev2(event):
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Invoices'))
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Swaps'))
async def swaps(event):
    text = (f"💼 <b>Сделки</b>\n\n"
            f"Если Вы хотите совершить <b>сделку</b> по обмену любой валюты, доступной в боте, с <b>другим пользователем</b>, но переживаете за безопасность сделки, создайте сделку с нужными вам параметрами и <b>отправьте её пользователю</b>, <b>с которым</b> хотите совершить обмен.\n\n"
            f"В этом случае бот выступит в роли гаранта сделки, и Ваши средства будут в безопасности.")

    buttons=[
                [
                    Button.inline('Создать', b'Create_Swap'),
                ],
                [
                    Button.inline('‹ Назад', b'Back'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Subscriptions'))
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'RocketPay'))
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Settings'))
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
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'NFT'))
async def nft(event):
    text = (f"🖼 <b>NFT</b>\n\n"
            f"Здесь Вы можете просматривать и управлять вашими NFT.\n"
            f"<b>Владение NFT</b> даёт Вам <b>скидки</b> и <b>бонусы</b> на предоставляемые нами услуги.\n"
            f"Каждое NFT даёт определённый процент скидки и дополнительного бонуса, также учитывайте то, что <b>бонусы и скидки от каждого NFT суммируются</b>, что даёт Вам ещё большую выгоду.\n\n"
            f"Реферальный процент: <b>10%</b>\n"
            f"Скидки на все комиссии: <b>0%</b>\n"
            f"Вес: <b>0</b>")

    buttons=[
                [
                    Button.url('Купить NFT', 'https://t.me/ton_rocket_presale_bot'),
                ],
                [
                    Button.inline('‹ Назад', b'Wallet'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'LinkWallet'))
async def linkwallet(event):
    text = (f"🔌 <b>Привязать кошелёк</b>\n\n"
            f"Вы можете <b>привязать свои TON кошелёк</b> к нашему боту для удобства вывода монет с нашего бота на свой кошелёк.")

    buttons=[
                [
                    Button.url('Привязать кошелёк', 'https://t.me/xrocket/cex?startapp=connect-wallet-ton'),
                ],
                [
                    Button.inline('Привязанные кошельки', b'Active'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Listing'))
async def Listing(event):
    text = (f"☄️ <b>Заявка на листинг токена</b>\n\n"
            f"Для подачи заявки <b>на листинг Вашего токена</b> необходимо указать требуемые от нас данные, а также <b>иметь на Вашем балансе в боте</b> сумму, необходимую для оплаты листинга в размере в <b>46297 XROCK (4 000.1$)</b> (20% скидка) или <b>5000 USDT</b>.\n\n"
            f"После подачи заявки будет принято решение о листинге, в случае отказа сумма оплаты за листинг <b>будет возвращена Вам на баланс</b>.\n\n"
            f"🎈 Также обратите внимание, что <b>в случае листинга</b> Вам потребуется <b>произвести оплату</b> в токенах эквивалентную стоимости листинга, т.е. <b>оплатить сумму 5000 USD в токенах</b>.\n\n"
            f"<b>Наши требования:</b>\n"
            f"· проект должен существовать <b>более 1 месяца</b>\n"
            f"· обладать дорожной картой, токеномикой и сообществом\n\n"
            f"Вся детальная информация доступна по <a href='https://telegra.ph/xrocket---usloviya-listinga-10-26'><b>этой ссылке</b></a>")

    buttons=[
                [
                    Button.inline('💡 Подробнее о листинге', b'Info'),
                ],
                [
                    Button.inline('Создать заявку', b'Create'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'History'))
async def history(event):
    text = (f"📄 <b>История</b>\n\n"
            f"Выберите интересующий пункт истории Вашего кошелька.")

    buttons=[
                [
                    Button.inline('📥 Пополнения', b'Deposit'),
                    Button.inline('📤 Выводы', b'Withdraw'),
                ],
                [
                    Button.inline('💸 Переводы', b'Transfer'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Language'))
async def language(event):
    text = (f"⚙️ <b>Настройки</b>\n\n"
            f"Ваш язык: <b>🇷🇺 Русский</b>\n\n"
            f"<b>Выберите язык:</b>")

    buttons=[
                [
                    Button.inline('Английский', b'Change_EN'),
                    Button.inline('· Русский ·', b'Change_RU'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'BotCurrency'))
async def botcurrency(event):
    text = (f"⚙️ <b>Настройки</b>\n\n"
            f"Текущая валюта: <b>USD · $</b>\n\n"
            f"<b>Выберите валюту, в которой будет отображаться баланс:</b>")

    buttons=[
                [
                    Button.inline('· USD $ ·', b'Currency_1'),
                    Button.inline('RUB ₽', b'Currency_2'),
                    Button.inline('EUR €', b'Currency_3'),
                    Button.inline('BYN Br', b'Currency_4'),
                ],
                [
                    Button.inline('UAH ₴', b'Currency_5'),
                    Button.inline('GBP £', b'Currency_6'),
                    Button.inline('CNY ¥', b'Currency_7'),
                    Button.inline('KZT ₸', b'Currency_8'),
                ],
                [
                    Button.inline('UZS Som', b'Currency_9'),
                    Button.inline('GEL ₾', b'Currency_10'),
                    Button.inline('TRY ₺', b'Currency_11'),
                    Button.inline('KRW ₩', b'Currency_12'),
                ],
                [
                    Button.inline('TJS с', b'Currency_13'),
                    Button.inline('PLN zł', b'Currency_14'),
                    Button.inline('THB ฿', b'Currency_15'),
                    Button.inline('KGS Som', b'Currency_16'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'HideBalances'))
async def hidebalances(event):
    text = (f"⚙️ <b>Настройки</b>\n\n"
            f"Выберите как отображать баланс Вашего кошелька:")

    buttons=[
                [
                    Button.inline('✅ Показывать все', b'Balances_SHOWALL'),
                ],
                [
                    Button.inline('Скрывать нулевые', b'Balances_HIDEZEROS'),
                ],
                [
                    Button.inline('Скрывать менее 1 USD', b'Balances_HIDELESS'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'DevChat'))
async def devchat(event):
    text = (f"🤖 <b>Rocket Pay</b>\n\n"
            f"Для вступления в чат разработчиков требуется оформить подписку, оплатить можно в TON или USDT.\n\n"
            f"<b>Выберите валюту оплаты:</b>")

    buttons=[
                [
                    Button.url('TON', 'https://t.me/+mA9IoHSdvIRhZjFi'),
                    Button.url('USDT', 'https://t.me/+Tzm3cgbDZR0zZWMy'),
                ],
                [
                    Button.inline('‹ Назад', b'RocketPay'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)


@client.on(events.CallbackQuery(data=b'Create_Swap'))
async def create_swap(event):
    text = (f"💼 <b>Сделки</b>\n\n"
            f"<b>Выберите валюту которую хотите обменять:</b>")

    buttons=[
                [
                    Button.inline('TON', b'fromCoin_1'),
                    Button.inline('USDT', b'fromCoin_30'),
                ],
                [
                    Button.inline('‹ Сделки', b'Swaps'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'BotExchange'))
async def botexchange(event):
    text = (f"💱 <b>Биржа</b>\n\n"
            f"Торгуйте любой криптовалютой, которая есть в боте, как на обычной бирже.\n\n"
            f"Комиссия составляет <b>0.1%</b> для мейкеров и <b>0.15%</b> для тейкеров <b>с получаемой</b> суммы ордера.")

    buttons=[
                [
                    Button.inline('Создать ордер', b'CreateOrder'),
                ],
                [
                    Button.inline('Книга ордеров', b'OrderBook'),
                ],
                [
                    Button.inline('Мои ордера', b'MyOrders'),
                ],
                [
                    Button.inline('‹ Назад', b'ExchangeV2'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'CreateOrder'))
@client.on(events.CallbackQuery(data=b'OrderBook'))
async def createorder_orderbook(event):
    ton_usdt_price = get_ton_usd_price()

    text = (f"💱 <b>Биржа</b>\n\n"
            f"Выберите интересующую Вас пару для <b>создания ордера</b>:")

    buttons=[
                [
                    Button.inline(f'TON/USDT · {ton_usdt_price} USDT', b'Pair_ton_usdt'),
                ],
                [
                    Button.inline('‹ Назад', b'BotExchange'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Settings_Exchange'))
async def settings_sxchange(event):
    text = (f"💱 <b>Настройки биржи</b>\n\n"
            f"Управляйте своим ключом Exchange API, а так же настройками уведомлений")

    buttons=[
                [
                    Button.inline('API Token', b'ApiKey'),
                ],
                [
                    Button.inline('Настройки уведомлений', b'Notifications'),
                ],
                [
                    Button.url('Документация Exchange Api', 'https://trade.ton-rocket.com/api'),
                ],
                [
                    Button.inline('‹ Назад', b'ExchangeV2'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'ApiKey'))
async def apikey(event):
    text = (f"💱 <b>Настройки биржи</b>\n\n"
            f"Используйте <b>Exchange API</b> для автоматизации Вашей торговли на бирже.\n\n"
            f"Создавайте или управляйте своим ключом доступа к <b>Exchange API</b>\n\n"
            f"💳 <b>Ваш API Token:</b> <code>2c8YFrsgccg3aJifSg45Z7cuWTXEd6</code>")

    buttons=[
                [
                    Button.inline('🔄 Перевыпустить API Token', b'RenewKey'),
                ],
                [
                    Button.inline('🌐 Вебхуки: выкл', b'Webhooks'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings_Exchange'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Notifications'))
async def notifications(event):
    text = (f"💱 <b>Настройки биржи</b>\n\n"
            f"Установите желаемые настройки уведомлений")

    buttons=[
                [
                    Button.inline('Частичное исполнение: Со звуком', b'NotificationPartially'),
                ],
                [
                    Button.inline('Полное исполнение: Со звуком', b'NotificationFull'),
                ],
                [
                    Button.inline('‹ Назад', b'Settings_Exchange'),
                ],
            ]
    
    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Cheques'))
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

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Personal'))
async def personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    user_data["creating_cheque"] = False
    save_user_data(user_id, user_data)

    cheque_count = len([cheque for cheque in user_data["cheques"] if cheque["status"] == "created"])

    text = (f"🏷 <b>Персональные чеки</b>\n\n"
            f"Создайте персональный чек, чтобы отправить сообщение с монетами выбранному Вами пользователю.")

    buttons = [
        [
            Button.inline('📝 Создать чек', b'Create_Personal'),
        ],
        [
            Button.inline('‹ Назад', b'Cheques'),
        ],
    ]

    if cheque_count > 0:
        buttons.insert(1, [Button.inline(f'Мои персональные чеки · {cheque_count}', b'My_Personal_Cheques')])

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'Create_Personal'))
async def create_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    buttons = []
    kok = []
    if user_data["balance_ton"] > 0:
        kok.append(Button.inline('TON', b'ton_personal'))
    if user_data["balance_usdt"] > 0:
        kok.append(Button.inline('USDT', b'usdt_personal'))
    
    if kok:
        buttons.append(kok)

    buttons.append([Button.inline('‹ Назад', b'Personal')])

    if not buttons:
        text = (f"🏷 <b>Персональный чек</b>\n\n"
                f"💩 <b>Ваш баланс пуст</b>")
    else:
        text = (f"🏷 <b>Персональный чек</b>\n\n"
                f"<b>Выберите валюту чека:</b>")

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'ton_personal'))
async def ton_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    ton_usd_price = get_ton_usd_price()
    balance_ton_price_in_usd = user_data["balance_ton"] * ton_usd_price

    user_data["creating_cheque"] = True
    user_data["creating_cheque_currency"] = "TON"
    save_user_data(user_id, user_data)

    balance_ton_display = f"{user_data['balance_ton']:.2f}".rstrip('0').rstrip('.')
    balance_ton_price_display = f"{balance_ton_price_in_usd:.2f}".rstrip('0').rstrip('.')

    text = (f"🏷 <b>Персональный чек</b>\n\n"
            f"Сколько TON Вы хотите отправить пользователю с помощью чека?\n\n"
            f"<b>Максимум:</b> <b>{balance_ton_display} TON ({balance_ton_price_display}$)</b>\n"
            f"Минимум: <b>0.00001 TON</b>\n\n"
            f"<b>Введите сумму чека в TON:</b>")

    buttons = [
        [Button.inline(f'Максимум · {balance_ton_display} TON ({balance_ton_price_display}$)', b'Max_ton_personal')],
        [Button.inline('‹ Выбор валюты', b'Create_Personal')],
        [Button.inline('‹ Назад', b'Personal')],
    ]

    message = await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    user_data["last_message_id"] = message.id
    save_user_data(user_id, user_data)

@client.on(events.CallbackQuery(data=b'Max_ton_personal'))
async def max_ton_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    
    cheque_id = generate_cheque_id()
    cheque = {
        "id": cheque_id,
        "type": "personal",
        "amount": user_data["balance_ton"],
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
        [Button.inline('✅ Подтверждаю', f'Success_create_ton_personal:{user_data["balance_ton"]}'), Button.inline('❌ Отклоняю', b'Personal')],
        [Button.inline('‹ Изменить сумму', b'ton_personal')],
        [Button.inline('‹ Назад', b'Personal')]
    ]

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(pattern=b'Success_create_ton_personal:(.*)'))
async def success_create_ton_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    data = float(event.data.decode('utf-8').split(':')[1])
    amount_str = str(data).rstrip('0').rstrip('.') if '.' in str(data) else str(data)
    amount = float(amount_str)

    if amount > user_data["balance_ton"]:
        return

    cheque_id = generate_cheque_id()
    cheque = {
        "id": cheque_id,
        "type": "personal",
        "amount": amount,
        "currency": "TON",
        "status": "created"
    }
    user_data["cheques"].append(cheque)
    cheque_ton_amount_price_in_usd = cheque["amount"] * get_ton_usd_price()
    user_data["balance_ton"] -= amount
    save_user_data(user_id, user_data)

    user_data["creating_cheque"] = False
    save_user_data(user_id, user_data)

    cheque_amount_display = f"{cheque['amount']:.2f}".rstrip('0').rstrip('.')
    cheque_price_display = f"{cheque_ton_amount_price_in_usd:.2f}".rstrip('0').rstrip('.')

    text = (f"🏷 <b>Персональный чек</b>\n\n"
            f"<b>Сумма чека</b>: {cheque_amount_display} TON ({cheque_price_display}$)\n\n"
            f"‼️ <b>Никогда не делайте скриншот и не передавайте ссылку на чек людям, которым вы не доверяете.</b> "
            f"Делая это, вы передаете средства в этом чеке безвозмездно, без гарантий получить что-то взамен. "
            f"Мошенники могут использовать это, чтобы получить ваши монеты\n\n"
            f"<b>Ссылка на чек</b>: <span class='tg-spoiler'>t.me/{bot_username}?start={cheque_id}</span>")

    buttons=[
                [
                    types.KeyboardButtonSwitchInline(
                        '💸 Отправить', 
                        f'{cheque_id}')
                ],
                [
                    Button.inline('Показать QR-код', f'Qr:{cheque_id}'),
                ],
                [
                    Button.inline('Добавить описание', f'Comment:{cheque_id}'),
                ],
                [
                    Button.inline('Привязать к пользователю', f'Lock:{cheque_id}'),
                ],
                [
                    Button.inline('Удалить', f'Delete:{cheque_id}'),
                ],
                [
                    Button.inline('‹ Назад', b'Personal'),
                ],
            ]

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    if all_logs:
        print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) создал чек на {cheque_amount_display} TON, ID чека: {cheque_id}")

@client.on(events.CallbackQuery(pattern=b'Success_create_usdt_personal:(.*)'))
async def success_create_usdt_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    data = float(event.data.decode('utf-8').split(':')[1])
    amount_str = str(data).rstrip('0').rstrip('.') if '.' in str(data) else str(data)
    amount = float(amount_str)

    if amount > user_data["balance_usdt"]:
        return

    cheque_id = generate_cheque_id()
    cheque = {
        "id": cheque_id,
        "type": "personal",
        "amount": amount,
        "currency": "USDT",
        "status": "created"
    }
    user_data["cheques"].append(cheque)
    user_data["balance_usdt"] -= amount
    user_data["creating_cheque"] = False
    save_user_data(user_id, user_data)

    cheque_amount_display = f"{cheque['amount']:.2f}".rstrip('0').rstrip('.')

    text = (f"🏷 <b>Персональный чек</b>\n\n"
            f"<b>Сумма чека</b>: {cheque_amount_display} USDT ({cheque_amount_display}$)\n\n"
            f"‼️ <b>Никогда не делайте скриншот и не передавайте ссылку на чек людям, которым вы не доверяете.</b> "
            f"Делая это, вы передаете средства в этом чеке безвозмездно, без гарантий получить что-то взамен. "
            f"Мошенники могут использовать это, чтобы получить ваши монеты\n\n"
            f"<b>Ссылка на чек</b>: <span class='tg-spoiler'>t.me/xRokeetBot?start={cheque_id}</span>")

    buttons=[
                [
                    types.KeyboardButtonSwitchInline(
                        '💸 Отправить', 
                        f'{cheque_id}')
                ],
                [
                    Button.inline('Показать QR-код', f'Qr:{cheque_id}'),
                ],
                [
                    Button.inline('Добавить описание', f'Comment:{cheque_id}'),
                ],
                [
                    Button.inline('Привязать к пользователю', f'Lock:{cheque_id}'),
                ],
                [
                    Button.inline('Удалить', f'Delete:{cheque_id}'),
                ],
                [
                    Button.inline('‹ Назад', b'Personal'),
                ],
            ]

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    if all_logs:
        print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) создал чек на {cheque_amount_display} USDT, ID чека: {cheque_id}")

@client.on(events.CallbackQuery(pattern=b'Comment:'))
async def add_comment(event):
    button = event.data.decode()
    cheque_id = button.split(':')[1]
    message = await event.edit(
        text=(f"🏷 <b>Персональный чек</b>\n\n"
              f"<i>Введите описание, которое хотите прикрепить к персональному чеку.</i>\n\n"
              f"<i>Максимальная длина - <b>1000 символов</b></i>"),
        buttons=[Button.inline('‹ Назад', f'cheque_{cheque_id}')],
        parse_mode="html"
    )
    user_data = load_user_data(event.sender_id)
    user_data['adding_comment'] = cheque_id
    user_data["last_message_id"] = message.id
    save_user_data(event.sender_id, user_data)

@client.on(events.CallbackQuery(pattern=b'rm_comment:'))
async def remove_comment(event):
    button = event.data.decode()
    cheque_id = button.split(':')[1]
    user_data = load_user_data(event.sender_id)

    for cheque in user_data['cheques']:
        if cheque['id'] == cheque_id:
            cheque['comment'] = ''
            break

    save_user_data(event.sender_id, user_data)
    if all_logs:
        print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) удалил описание из чека, ID чека: {cheque_id}")

    await showkok(event, cheque_id)

@client.on(events.CallbackQuery(pattern=b'Delete:'))
async def delete_cheque(event):
    button = event.data.decode()
    cheque_id = button.split(':')[1]
    user_data = load_user_data(event.sender_id)

    cheque = next((cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id), None)
    
    if not cheque:
        await event.reply("Чек с указанным ID не найден.")
        return

    amount = cheque['amount']
    currency = cheque['currency']

    if currency == "TON":
        user_data['balance_ton'] += amount
    elif currency == "USDT":
        user_data['balance_usdt'] += amount   
    
    user_data['cheques'] = [chq for chq in user_data['cheques'] if chq['id'] != cheque_id]
    save_user_data(event.sender_id, user_data)

    await event.answer("Персональный чек успешно удален")
    if all_logs:
        print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) удалил чек, ID чека: {cheque_id}")

    cheque_count = len([cheque for cheque in user_data["cheques"] if cheque["status"] == "created"])

    text = (f"🏷 <b>Персональные чеки</b>\n\n"
            f"Создайте персональный чек, чтобы отправить сообщение с монетами выбранному Вами пользователю.")

    buttons = [
        [
            Button.inline('📝 Создать чек', b'Create_Personal'),
        ],
        [
            Button.inline('‹ Назад', b'Cheques'),
        ],
    ]

    if cheque_count > 0:
        buttons.insert(1, [Button.inline(f'Мои персональные чеки · {cheque_count}', b'My_Personal_Cheques')])

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(pattern=b'Qr:(.*)'))
async def show_qr_code(event):
    user_data = load_user_data(event.sender_id)
    cheque_id = event.pattern_match.group(1).decode('utf-8')
    cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
    amount = float(cheque["amount"])
    amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
    amount_in_usd = amount * get_ton_usd_price()

    comment = cheque.get('comment', '')
    tied_to_user = cheque.get('tied_to_user', {})

    qr_url = f"https://api.qrcode-monkey.com/qr/custom?data=https%3A%2F%2Ft.me%2FxRokeetBot%3Fstart%3D{cheque_id}&config=%7B%22body%22%3A%22circular%22%2C%22eye%22%3A%22frame13%22%2C%22eyeBall%22%3A%22ball15%22%2C%22bodyColor%22%3A%22%23159af6%22%2C%22bgColor%22%3A%22%23FFFFFF%22%2C%22eye1Color%22%3A%22%23159af6%22%2C%22eye2Color%22%3A%22%23159af6%22%2C%22eye3Color%22%3A%22%23159af6%22%2C%22eyeBall1Color%22%3A%22%23159af6%22%2C%22eyeBall2Color%22%3A%22%23159af6%22%2C%22eyeBall3Color%22%3A%22%23159af6%22%7D&size=1500"

    text = (f"<a href='{qr_url}'>‍</a>🏷 <b>Персональный чек</b>\n\n"
            f"<b>Сумма чека:</b> {amount_str} {cheque['currency']} ({amount_in_usd:.2f}$)\n\n")

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
            Button.inline('Скрыть QR-код', f'HideQr:{cheque_id}'),
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

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=True)

@client.on(events.CallbackQuery(pattern=b'HideQr:(.*)'))
async def hide_qr_code(event):
    user_data = load_user_data(event.sender_id)
    cheque_id = event.pattern_match.group(1).decode('utf-8')
    cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
    amount = float(cheque["amount"])
    amount_str = f'{amount:.2f}'.rstrip('0').rstrip('.')
    amount_in_usd = amount * get_ton_usd_price()

    comment = cheque.get('comment', '')

    tied_to_user = cheque.get('tied_to_user', {})
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

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(pattern=b'Lock:'))
async def add_lock(event):
    button = event.data.decode()
    cheque_id = button.split(':')[1]
    message = await event.edit(
        text=(f"🏷 <b>Персональный чек</b>\n\n"
              f"Отправьте мне <b>@username</b> пользователя или перешлите любое сообщение от него."),
        buttons=[Button.inline('‹ Назад', f'cheque_{cheque_id}')],
        parse_mode="html"
    )
    user_data = load_user_data(event.sender_id)
    user_data['locking_cheque'] = cheque_id
    user_data["last_message_id"] = message.id
    save_user_data(event.sender_id, user_data)

@client.on(events.CallbackQuery(pattern=b'Unlock:'))
async def remove_lock(event):
    button = event.data.decode()
    cheque_id = button.split(':')[1]
    user_data = load_user_data(event.sender_id)
    cheque = next(cheque for cheque in user_data['cheques'] if cheque['id'] == cheque_id)
    if all_logs:
        print(f"[log] Пользователь {user_data['first_name']} (ID: {user_data['id']}) отвязал чек от пользователя {cheque['tied_to_user']['name']} (ID: {cheque['tied_to_user']['id']}), ID чека: {cheque['id']}")
    cheque.pop('tied_to_user', None)
    save_user_data(event.sender_id, user_data)

    await showkok(event, cheque_id)

@client.on(events.CallbackQuery(data=b'usdt_personal'))
async def usdt_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    user_data["creating_cheque"] = True
    user_data["creating_cheque_currency"] = "USDT"
    save_user_data(user_id, user_data)

    balance_USDT_display = f"{user_data['balance_usdt']:.2f}".rstrip('0').rstrip('.')

    text = (f"🏷 <b>Персональный чек</b>\n\n"
            f"Сколько USDT Вы хотите отправить пользователю с помощью чека?\n\n"
            f"<b>Максимум:</b> <b>{balance_USDT_display} USDT ({balance_USDT_display}$)</b>\n"
            f"Минимум: <b>0.00001 USDT</b>\n\n"
            f"<b>Введите сумму чека в USDT:</b>")

    buttons = [
        [Button.inline(f'Максимум · {balance_USDT_display} USDT ({balance_USDT_display}$)', b'Max_usdt_personal')],
        [Button.inline('‹ Выбор валюты', b'Create_Personal')],
        [Button.inline('‹ Назад', b'Personal')],
    ]

    message = await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    user_data["last_message_id"] = message.id
    save_user_data(user_id, user_data)

@client.on(events.CallbackQuery(data=b'Max_usdt_personal'))
async def max_usdt_personal(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    
    cheque_id = generate_cheque_id()
    cheque = {
        "id": cheque_id,
        "type": "personal",
        "amount": user_data["balance_usdt"],
        "currency": "USDT",
        "status": "created"
    }
    cheque_amount_display = f"{cheque['amount']:.2f}".rstrip('0').rstrip('.')

    text = (f"🏷 <b>Персональный чек</b>\n\n"
            f"<b>Сумма чека</b>: {cheque_amount_display} USDT ({cheque_amount_display}$)\n\n"
            f"<b>🔸 Пожалуйста, подтвердите корректность данных:</b>")

    buttons = [
        [Button.inline('✅ Подтверждаю', f'Success_create_usdt_personal:{user_data["balance_usdt"]}'), Button.inline('❌ Отклоняю', b'Personal')],
        [Button.inline('‹ Изменить сумму', b'usdt_personal')],
        [Button.inline('‹ Назад', b'Personal')]
    ]

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(data=b'My_Personal_Cheques'))
async def my_personal_cheques(event):
    user_id = event.sender_id
    user_data = load_user_data(user_id)
    cheques = [cheque for cheque in user_data["cheques"] if cheque["status"] == "created"]

    text = (f"🏷 <b>Персональные чеки\n\n"
            f"Список Ваших персональных чеков:</b>")

    buttons = []
    for cheque in cheques:
        amount = f'{cheque["amount"]}'.rstrip('0').rstrip('.')
        if cheque["currency"] == "USDT":
            amount_in_usd = amount
        else:
            amount_in_usd = f'{cheque["amount"] * get_ton_usd_price():.2f}'.rstrip('0').rstrip('.')

        description_parts = [f'{amount} {cheque["currency"]} ({amount_in_usd}$)']
        
        if "tied_to_user" in cheque:
            tied_user = cheque["tied_to_user"]
            description_parts.append(f'· {tied_user["name"]}')
        
        if "comment" in cheque:
            description_parts.append(f'· {cheque["comment"]}')
        
        description_text = ' '.join(description_parts)

        buttons.append([
            Button.inline(
                description_text, 
                f'cheque_{cheque["id"]}'
            )
        ])

    buttons.append([Button.inline('‹ Назад', b'Personal')])

    await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)

@client.on(events.CallbackQuery(pattern=b'cheque_'))
async def show_cheque(event):
    button = event.data.decode()
    cheque_id = f"t_{button.split('_')[2]}"
    user_id = event.sender_id
    user_data = load_user_data(user_id)

    cheque = None
    for c in user_data["cheques"]:
        if c["id"] == f"{cheque_id}":
            cheque = c
            break

    if cheque is None:
        await event.respond("<b>Чек не найден. (what??)</b>", parse_mode="html")
        return

    amount = f'{cheque["amount"]}'.rstrip('0').rstrip('.')
    amount_in_usd = cheque["amount"] if cheque["currency"] == "USDT" else cheque["amount"] * get_ton_usd_price()
    comment = cheque.get('comment', '')
    tied_to_user = cheque.get('tied_to_user', {})
    text = (f"🏷 <b>Персональный чек\n\n"
            f"Сумма чека:</b> {amount} {cheque['currency']} ({amount_in_usd:.2f}$)\n\n")

    if tied_to_user:
        text += f"Только для <a href='tg://user?id={tied_to_user['id']}'><b>{tied_to_user['name']}</b></a>\n\n"

    if comment:
        text += f"💬 {comment}\n\n"

    text += (f"‼️ <b>Никогда не делайте скриншот и не передавайте ссылку на чек людям, которым вы не доверяете.</b> Делая это, вы передаете средства в этом чеке безвозмездно, без гарантий получить что-то взамен. Мошенники могут использовать это, чтобы получить ваши монеты\n\n"
             f"<b>Ссылка на чек:</b>\n<span class='tg-spoiler'>t.me/{bot_username}?start={cheque_id}</span>")

    buttons=[
        [
            types.KeyboardButtonSwitchInline('💸 Отправить', f'{cheque_id}')
        ],
        [
            Button.inline('Показать QR-код', f'Qr:{cheque_id}'),
        ],
    ]

    if comment:
        buttons.append([Button.inline('Убрать описание', f'rm_comment:{cheque_id}')])
    elif not comment:
        buttons.append([Button.inline('Добавить описание', f'Comment:{cheque_id}')])

    if tied_to_user:
        buttons.append([Button.inline('Отвязать от пользователя', f'Unlock:{cheque_id}')])
    else:
        buttons.append([Button.inline('Привязать к пользователю', f'Lock:{cheque_id}')])

    buttons.extend([
        [Button.inline('Удалить', f'Delete:{cheque_id}')],
        [Button.inline('‹ Назад', b'My_Personal_Cheques')],
    ])

    message = await event.edit(text, buttons=buttons, parse_mode='html', link_preview=False)
    user_data["last_message_id"] = message.id
    save_user_data(user_id, user_data)

@client.on(events.CallbackQuery(data=b'newsletter'))
async def newsletter(event):
    if event.sender_id != admin_id:
        return

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

    await event.edit(text, parse_mode="html")

    async with client.conversation(event.sender_id) as conv:
        await conv.send_message(f'💬 <b>Отправьте сообщение для рассылки. Или<b> "<code>отменить</code>" <b>для отмены</b>\n\n'
                                f'✅ <i>(Поддерживаются любые сообщения текст, медиа, стикеры, кружки, файлы, даже сообщения с URL кнопками!!)</i>', parse_mode="html")

        while True:
            response = await conv.get_response()

            if response.text.lower() == "отменить":
                await conv.send_message('😕 <b>Рассылка отменена</b>', parse_mode="html")
                return

            gavgavgav = response #сорри за то что в некоторых местах такие названия 😔 просто мне так захотелось почему то...
            break

        await send_newsletter(gavgavgav)
        await conv.send_message('👾 <i>Рассылка успешно завершена!</i>', parse_mode="html")