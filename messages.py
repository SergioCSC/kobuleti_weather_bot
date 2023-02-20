import config as cfg


START_TEXT = \
    f'Здравствуйте! Бот показывает погоду сейчас и на несколько дней вперёд в выбранном вами месте' \
    f' (инфа с сайтов openweathermap.org и meteoblue.com).' \
    f'\n\n\n*Основные команды*' \
    f'\n\n🧑‍💻 _*/город*_ — показывает погоду в городе (например, _*/караганда*_)' \
    f'\n\n🧑‍💻 _*/here*_ (она же команда _*/тут*_) — показывает погоду в вашей геопозиции' \
    f' (работает только в личке).' \
    f'\n\n🧑‍💻 _*/dark*_ (она же _*/тьма*_) — поменять цвет картинки со светлого на тёмный и обратно' \
    f'\n\n\n*Сводки погоды*' \
    f'\n\nМожно настроить бота регулярно отправлять вам сводки погоды.' \
    f' Для этого нужно сотворить *список городов* и указать *время*,' \
    f' когда отправлять сводки.' \
    f'\n\n🧑‍💻 _*/list*_ (она же _*/список*_) — настройка списка городов в сводке' \
    f'\n\n🧑‍💻 _*/time*_ (она же _*/шли*_) — настройка времени отправки сводок'


ABOUT_TIME_COMMAND_TEXT = f'🧑‍💻 _*/time 13*_ (или _*/шли 13*_) — присылать сводку' \
    f' погоды каждый день в 13 часов' \
    f'\n🧑‍💻 _*/time 13.30*_ — каждый день в 13 часов 30 минут ' \
    f'\n🧑‍💻 _*/шли сб 13.30*_ — каждую субботу в 13 часов 30 минут' \
    f'\n\n🧑‍💻 _*/time clear*_ (или _*/шли никогда*_) — не отправлять регулярные сводки погоды' \
    f'\n\n🧑‍💻 _*/time*_ (она же _*/шли*_) — показать это описание и список уже настроенных сводок' \
    f'\n\n🧑‍💻 _*/home караганда*_ (она же _*/дом караганда*_) — установить часовой пояс' \
    f' как в Караганде (чтобы бот понимал, когда именно вам присылать сообщения)' \
    f'\n\n\nА вот чтобы настроить список городов в сводке, наберите команду 🧑‍💻 _*/list*_ (она же _*/список*_)'


ABOUT_LIST_COMMAND_TEXT = \
    f'*Управление списком городов*' \
    f'\n\n🧑‍💻 _*/add город*_ (она же _*/добавь город*_) — добавить город в список.' \
    f' Например, _*/добавь караганда*_' \
    f'\n\n🧑‍💻 _*/list*_ (она же _*/список*_) — показать список уже добавленных городов' \
    f'\n\n🧑‍💻 _*/report*_ (она же _*/сводка*_) — показать погоду в городах из списка' \
    f'\n\n🧑‍💻 _*/clear*_ (она же _*/очисти*_) — удалить все города из списка' \
    f'\n\n\nА вот чтобы настроить время получения сводок, наберите команду' \
    f' _*/time*_ (она же _*/шли*_)'


NOT_FOUND_WEATHER_TEXTS = [

    f'Чёт я не нашла.' \
    f' Галя! Гааа-ляяя! Ты слышала про такой город?' \
    f' C кем ты туда ездила? А, я так и думала. А чего меня не позвала? ...' \
    f'\n\nОй, сударь, вы ещё здесь? Извините, такого города не существует',

    f'Мне лень',

    f'Ну вот, опять вставать, куда-то идти ...',

    f'Сударь, вы погоду на улице видели? Вы правда хотите, чтобы' \
    f' я встала и пошла узнавать вам погоду в такую погоду?',

    f'Извините, сегодня не могу. Ох, какая нынче чача у Бачухи ...',

    f'Закрыты на переучёт товара',

    f'Уехала на десятую международную конференцию в Гааге. Выступила с пакетом' \
    f' конструктивных предложений, направленных на углубление процесса интеграции.' \
    f' Не до погоды мне, сударь',

    f'Ох, ребята, там ... нет, я не могу это произнести. В общем, держитесь.' \
    f' Хорошего вам настроения!',

    f'Увольте, сударь. Не велено вас пущать',

    f'Добрый день, сударь! Погода выдаётся в любом нашем отделении' \
    f' в г. Москва без очередей и выходных!' \
    f' Спасибо за использование наших услуг.' \
    f' Оцените наш сервис, когда вернётесь из г. Москва!',

    f'Вот зачем вам погода? Бегать, на велике кататься, парки посещать?' \
    f' Пустое это всё. А давайте лучше вместе читать Фихтенгольца с выражением',

    f'А помнишь ли ты старенький приёмник из детства, который бодрым' \
    f' дикторским голосом' \
    f' зачитывал, что в Екатеринбурге переменная облачность,' \
    f' в Ременаме дожди? А теперь у тебя я. Извини ...',
]

NOT_FOUND_WEATHER_IMAGE_TEXT = '\n\nМожно ваш паспорт? Спасибо. Таааак ...' \
    f' Галя, не видишь, я занята. Что там у вас  ... аааа, ну конечно!' \
    f' А вы вообще в курсе, что вам никакие графики никаких температур не положены?' \
    f' Да, совсем. Не задерживайте очередь.' \
    f' Если вам так надо,' \
    f' подходите завтра к 8 утра в регистратуру с анализами.' \
    f' За результатами через 60 рабочих дней. Что вам ещё?' \
    f' Нет, через госуслуги нельзя. До свидания.\n\nИшь, прогноз погоды им подавай'

EMPTY_ADD_TEXT = f'Здравствуйте. Кажется, вы нажали команду\n\n_*/%s*_\n\nв меню.' \
    f' Вам-то хорошо, нажали и нажали. А наш департамент' \
    f' на ушах: все хотят знать, какой город вы хотите добавить' \
    f' в напоминалки. Все бегают, шумят, волосы рвут.' \
    f' Ставки делают, морды бьют. Работа встала. И никто ничего' \
    f' не знает, никто не за что не отвечает. Что за народ!' \
    f' можно вас попросить сказать им уже город, а то они всё тут разнесут?' \
    f' Ну, например, так: \n\n🧑‍💻 _*/add Ярославль*_\n\nили:' \
    f'\n\n🧑‍💻 _*/добавь Ярославль*_'

CITY_CITY_TEXT = f'Добро пожаловать на метеостанцию. Располагайтесь,' \
    f' чайку? Унты не ставьте близко к камину, сядут-с ... ' \
    f' Вы какие сигары предпочитаете, La Gloria Cubana? Romeo y Julieta?' \
    f' Простите, конечно, перехожу к вашему делу.' \
    f' Вы точно хотите послать гонцов в город city? Да, мои парни, конечно,' \
    f' могут и не такое, и собаки хорошо отдохнули. Только, вот, не хотите ли,' \
    f' вместо мифического\n\n_*/city*_\n\n, узнать погоду в городе\n\n🧑‍💻 _*/Оймякон*_\n\n?' \
    f' Или, допустим, в\n\n/🧑‍💻 _*Могадишо*_\n\n? Вы, кстати, были в Могадишо?' \
    f' Я вот вам очень советую. Очень, знаете ли, хорошее место, чтобы там' \
    f' не бывать. Я вот там не был и видите, как мне это понравилось ...' \
    f' Эх, да ... Вот же ж какого времени не было ... Хорошо.'

BUTTON_WEATHER_HERE_TEXT = f'Погода прямо тут'

HAVE_TO_THINK_TEXT = f'бегу на вышку ...'

TOO_MANY_CITIES_TEXT = f'Прошу прощения, сэр. К сожалению, в настоящий момент все операторы заняты.' \
    f' У нас тут дебаты, стоит ли ограничивать число городов в сводке числом' \
    f' {cfg.MAX_SAVED_CITIES_PER_USER}' \
    f' или же гори всё синим пламенем. Честно говоря, если разрешить много городов,' \
    f' это может вылиться в копеечку.' \
    f' Так что пока, если вы хотите добавить новый город,' \
    f' предлагаю удалить из сводки старые командой\n\n🧑‍💻 _*/clear*_,' \
    f' она же\n\n🧑‍💻 _*/очисти*_'