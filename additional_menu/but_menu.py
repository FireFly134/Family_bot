from telegram import ReplyKeyboardMarkup

def eat(update, context, user_triger):
    reply_keyboard = [['Продукт', 'Категории', 'Частота'], ['Отменить']]
    sms = "Тут можно выбрать или добавить новые 'Продукт', 'Категории' и периодичность заказа данных продуктов"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def products(update, context, user_triger):
    reply_keyboard = [['Добавить новый продукт', 'Удалить продукт', 'Посмотреть продукты'], ['Отменить']]
    user_triger[update.effective_chat.id] = {
        'triger': "products",
        'New': False,
        'Delete': False,
        'step': 0,
        'link': 'None',
        'categories': 'None'
    }
    sms = "Скопируйте ссылку на товар и пришлите в сообщении"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def categories (update, context, user_triger):
    reply_keyboard = [['Добавить новую категорию', 'Удалить категорию', 'Посмотреть категории'], ['Отменить']]
    user_triger[update.effective_chat.id] = {
        'triger': "categories",
        'New': False,
        'Delete': False
    }
    sms = "Тут можно выбрать или добавить новые 'Продукт', 'Категории' и периодичность заказа данных продуктов"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))
def frequency (update, context, user_triger):
    reply_keyboard = [['Добавить новую частоту'], ['Отменить']]
    user_triger[update.effective_chat.id] = {
        'triger': "frequency",
        'New': False,
        'Delete': False
    }
    sms = "Тут можно выбрать или добавить новые 'Продукт', 'Категории' и периодичность заказа данных продуктов"
    context.bot.send_message(chat_id=update.effective_chat.id, text=sms,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                              one_time_keyboard=False))