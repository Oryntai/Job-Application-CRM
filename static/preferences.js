(function () {
  var THEME_KEY = "jobcrm-theme";
  var LANG_KEY = "jobcrm-lang";

  var TRANSLATIONS = {
    ru: {
      "Dashboard": "Дашборд",
      "Applications": "Отклики",
      "Kanban": "Канбан",
      "Companies": "Компании",
      "Reminders": "Напоминания",
      "Profile": "Профиль",
      "Logout": "Выйти",
      "Login": "Вход",
      "Sign up": "Регистрация",
      "Language": "Язык",
      "Dark mode": "Темная тема",
      "Light mode": "Светлая тема",
      "Quick add": "Быстро добавить",
      "New company": "Новая компания",
      "Search companies": "Поиск компаний",
      "Search role/company/notes": "Поиск по роли/компании/заметкам",
      "All statuses": "Все статусы",
      "All sources": "Все источники",
      "Location": "Локация",
      "Applied date (desc)": "Дата отклика (сначала новые)",
      "Applied date (asc)": "Дата отклика (сначала старые)",
      "Next action": "Следующее действие",
      "Priority": "Приоритет",
      "No applications found.": "Отклики не найдены.",
      "Edit": "Редактировать",
      "Open": "Открыть",
      "Move": "Переместить",
      "No cards": "Карточек нет",
      "Add event": "Добавить событие",
      "Add reminder": "Добавить напоминание",
      "Overview": "Обзор",
      "Company": "Компания",
      "Status": "Статус",
      "Source": "Источник",
      "Salary": "Зарплата",
      "Move status": "Изменить статус",
      "Note": "Комментарий",
      "Change": "Обновить",
      "Timeline events": "События",
      "No events.": "Событий нет.",
      "Status history": "История статусов",
      "No status changes yet.": "Изменений статуса пока нет.",
      "Details": "Детали",
      "Website": "Сайт",
      "Contacts": "Контакты",
      "No contacts.": "Контактов нет.",
      "No applications.": "Откликов нет.",
      "Reminders": "Напоминания",
      "No reminders.": "Напоминаний нет.",
      "Cancel": "Отменить",
      "Company form": "Форма компании",
      "Application form": "Форма отклика",
      "Application": "Отклик",
      "Save": "Сохранить",
      "Create reminder": "Создать напоминание",
      "Save reminder": "Сохранить напоминание",
      "Profile settings": "Настройки профиля",
      "Username": "Имя пользователя",
      "Password": "Пароль",
      "Confirm password": "Подтвердите пароль",
      "Sign in": "Войти",
      "Create account": "Создать аккаунт",
      "Already have an account?": "Уже есть аккаунт?",
      "No account yet?": "Еще нет аккаунта?",
      "Create one": "Создать",
      "Company": "Компания",
      "Primary contact": "Основной контакт",
      "Role title": "Название роли",
      "Job url": "Ссылка на вакансию",
      "Location type": "Формат работы",
      "Location text": "Город/локация",
      "Salary min": "Зарплата от",
      "Salary max": "Зарплата до",
      "Currency": "Валюта",
      "Applied date": "Дата отклика",
      "Outreach variant": "Вариант обращения",
      "Notes": "Заметки",
      "Next action at": "Следующее действие в",
      "Next action text": "Текст следующего действия",
      "Name": "Название",
      "Message": "Сообщение",
      "Remind at": "Напомнить в",
      "Channel": "Канал",
      "Timezone": "Часовой пояс",
      "Email notifications": "Уведомления по почте",
      "Telegram chat id": "Telegram chat id",
      "Draft": "Черновик",
      "Applied": "Отклик отправлен",
      "Screening": "Скрининг",
      "Interview": "Собеседование",
      "Test Task": "Тестовое задание",
      "Offer": "Оффер",
      "Rejected": "Отказ",
      "Withdrawn": "Отозвано",
      "Low": "Низкий",
      "Medium": "Средний",
      "High": "Высокий",
      "Remote": "Удаленно",
      "Hybrid": "Гибрид",
      "Onsite": "Офис",
      "HeadHunter": "HeadHunter",
      "LinkedIn": "LinkedIn",
      "Referral": "Реферал",
      "Company Site": "Сайт компании",
      "Other": "Другое",
      "Template A": "Шаблон A",
      "Template B": "Шаблон B",
      "Email": "Email",
      "Telegram": "Telegram",
      "PENDING": "В ОЖИДАНИИ",
      "SENT": "ОТПРАВЛЕНО",
      "FAILED": "ОШИБКА",
      "CANCELLED": "ОТМЕНЕНО",
      "Total applications": "Всего откликов",
      "Offers": "Офферы",
      "Due reminders": "Напоминаний на сегодня",
      "Overdue": "Просрочено",
      "Weekly streak": "Недель подряд",
      "weeks": "нед.",
      "Goal: applications": "Цель: отклики",
      "Goal: follow-ups": "Цель: фоллоу-апы",
      "Funnel": "Воронка",
      "Sources": "Источники",
      "Recent status changes": "Последние изменения статусов",
      "No changes yet.": "Изменений пока нет.",
      "Time in stage (hours)": "Время на этапе (часы)",
      "Insufficient data.": "Недостаточно данных.",
      "A/B outcomes": "A/B результаты",
      "Need more data to pick a winner.": "Нужно больше данных для выбора лидера.",
      "Reached": "Дошли до этапа",
      "Response rate": "Доля ответов",
      "Offer rate": "Доля офферов"
    }
  };

  var PREFIX_TRANSLATIONS = {
    ru: [
      ["Reminder for ", "Напоминание для "],
      ["New event for ", "Новое событие для "],
      ["Current winner: template ", "Текущий лидер: шаблон "],
      ["Jobs: ", "Вакансии: "],
      ["Applied: ", "Отклик: "],
      ["Next action: ", "Следующее действие: "]
    ]
  };

  function normalizeTheme(value) {
    return value === "dark" ? "dark" : "light";
  }

  function normalizeLanguage(value) {
    return value === "ru" ? "ru" : "en";
  }

  function dictionary(lang) {
    return TRANSLATIONS[lang] || {};
  }

  function translateKey(lang, key) {
    return dictionary(lang)[key] || key;
  }

  function translateWithPrefix(lang, text) {
    var rules = PREFIX_TRANSLATIONS[lang] || [];
    for (var i = 0; i < rules.length; i += 1) {
      var source = rules[i][0];
      var target = rules[i][1];
      if (text.startsWith(source)) {
        return target + text.slice(source.length);
      }
    }
    return text;
  }

  function translateElementText(el, lang) {
    if (!el || el.dataset.i18nSkip === "true") {
      return;
    }

    if (el.children.length > 0) {
      return;
    }

    if (!el.dataset.i18nOriginal) {
      el.dataset.i18nOriginal = (el.textContent || "").trim();
    }

    var original = el.dataset.i18nOriginal;
    if (!original) {
      return;
    }

    if (lang === "en") {
      el.textContent = original;
      return;
    }

    var exact = translateKey(lang, original);
    if (exact !== original) {
      el.textContent = exact;
      return;
    }

    if (original.endsWith(":")) {
      var withoutColon = original.slice(0, -1).trim();
      var translatedWithoutColon = translateKey(lang, withoutColon);
      if (translatedWithoutColon !== withoutColon) {
        el.textContent = translatedWithoutColon + ":";
        return;
      }
    }

    var prefixed = translateWithPrefix(lang, original);
    el.textContent = prefixed;
  }

  function translatePlaceholder(el, lang) {
    if (!el || !Object.prototype.hasOwnProperty.call(el, "placeholder")) {
      return;
    }
    if (!el.dataset.i18nPlaceholderOriginal) {
      el.dataset.i18nPlaceholderOriginal = el.placeholder || "";
    }
    var originalPlaceholder = el.dataset.i18nPlaceholderOriginal;
    if (!originalPlaceholder) {
      return;
    }
    el.placeholder = lang === "en" ? originalPlaceholder : translateKey(lang, originalPlaceholder);
  }

  function translateDocumentTitle(lang) {
    if (!document.documentElement.dataset.i18nTitleOriginal) {
      document.documentElement.dataset.i18nTitleOriginal = document.title;
    }
    var originalTitle = document.documentElement.dataset.i18nTitleOriginal;
    if (!originalTitle) {
      return;
    }
    document.title = lang === "en" ? originalTitle : translateKey(lang, originalTitle);
  }

  function updateThemeButtonLabel(lang) {
    var theme = normalizeTheme(document.documentElement.getAttribute("data-theme"));
    var nextModeKey = theme === "dark" ? "Light mode" : "Dark mode";
    var labelNode = document.getElementById("theme-toggle-label");
    var button = document.getElementById("theme-toggle");
    if (!labelNode || !button) {
      return;
    }
    labelNode.dataset.i18nKey = nextModeKey;
    labelNode.textContent = lang === "ru" ? translateKey(lang, nextModeKey) : nextModeKey;
    button.setAttribute("aria-label", labelNode.textContent);
  }

  function applyTheme(theme) {
    var normalizedTheme = normalizeTheme(theme);
    document.documentElement.setAttribute("data-theme", normalizedTheme);
    localStorage.setItem(THEME_KEY, normalizedTheme);
    updateThemeButtonLabel(normalizeLanguage(localStorage.getItem(LANG_KEY)));
  }

  function applyLanguage(lang) {
    var normalizedLanguage = normalizeLanguage(lang);
    localStorage.setItem(LANG_KEY, normalizedLanguage);
    document.documentElement.setAttribute("lang", normalizedLanguage);
    document.documentElement.setAttribute("data-lang", normalizedLanguage);

    var keyed = document.querySelectorAll("[data-i18n-key]");
    for (var i = 0; i < keyed.length; i += 1) {
      var element = keyed[i];
      var key = element.dataset.i18nKey;
      if (!key) {
        continue;
      }
      element.textContent = normalizedLanguage === "en" ? key : translateKey(normalizedLanguage, key);
    }

    var textNodes = document.querySelectorAll(
      "header a, header button, header label, main h1, main h2, main h3, main h4, main strong, main p, main li, main a, main label, main button, main option"
    );
    for (var j = 0; j < textNodes.length; j += 1) {
      var node = textNodes[j];
      if (node.closest("script, style")) {
        continue;
      }
      translateElementText(node, normalizedLanguage);
    }

    var placeholders = document.querySelectorAll("input[placeholder], textarea[placeholder]");
    for (var k = 0; k < placeholders.length; k += 1) {
      translatePlaceholder(placeholders[k], normalizedLanguage);
    }

    translateDocumentTitle(normalizedLanguage);
    updateThemeButtonLabel(normalizedLanguage);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var languageControl = document.getElementById("language-switch");
    var themeControl = document.getElementById("theme-toggle");

    var savedTheme = normalizeTheme(localStorage.getItem(THEME_KEY));
    var savedLanguage = normalizeLanguage(localStorage.getItem(LANG_KEY));

    if (!document.documentElement.getAttribute("data-theme")) {
      document.documentElement.setAttribute("data-theme", savedTheme);
    }

    if (languageControl) {
      languageControl.value = savedLanguage;
      languageControl.addEventListener("change", function (event) {
        applyLanguage(event.target.value);
      });
    }

    if (themeControl) {
      themeControl.addEventListener("click", function () {
        var current = normalizeTheme(document.documentElement.getAttribute("data-theme"));
        applyTheme(current === "dark" ? "light" : "dark");
      });
    }

    applyLanguage(savedLanguage);
    applyTheme(document.documentElement.getAttribute("data-theme") || savedTheme);
  });
})();
