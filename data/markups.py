import data.markupOptions as Options
import data.botInstruments as Bi
import data.dataLoader as Dl

# GROUP = Bi.create_inline_keyboard({
#     'Поставить учебную группу': Options.SET_GROUP,
# }, row_width=1
# )

set_group_elements = {}
for el in Dl.groups_names:
    set_group_elements[el] = Options.GROUP_INDEXES + el
SET_GROUP = Bi.create_inline_keyboard(set_group_elements, row_width=4, back_button=('Назад', Options.GO_TO_GROUP_START))

SCHEDULE = Bi.create_inline_keyboard({
    'Сегодня': Options.GET_SCHEDULE_TODAY,
    'Завтра': Options.GET_SCHEDULE_TOMORROW,
    'В определённый день': Options.GET_SCHEDULE_AT_DAY
}, row_width=1
)

week_days_elements = {}
for el in Dl.days:
    week_days_elements[el] = Options.WEEK_DAYS_INDEXES + el
WEEK_DAYS = Bi.create_inline_keyboard(week_days_elements, row_width=2, back_button=('Назад', Options.GO_TO_SCHEDULE_START))

WEEK_DAY_SCHEDULE = Bi.create_inline_keyboard(back_button=('Назад', Options.GET_SCHEDULE_AT_DAY))
TODAY_SCHEDULE = Bi.create_inline_keyboard(back_button=('Назад', Options.GO_TO_SCHEDULE_START))

CALLS = Bi.create_inline_keyboard({
    'Узнать ближайший звонок': Options.NEAREST_CALL,
    'Закрепить ближайший звонок': Options.PIN_NEAREST_CALL,
    'Расписание звонков сегодня': Options.CALLS_TODAY,
    'Расписание звонков в понедельник': Options.CALLS_MONDAY,
    'Расписание звонков в будни/субботу': Options.CALLS_ANOTHER_DAY,
})
GO_TO_CALLS = Bi.create_inline_keyboard(back_button=('Назад', Options.GO_TO_CALLS))
