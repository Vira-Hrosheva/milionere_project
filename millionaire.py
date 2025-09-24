import json
import random
import os
from typing import List, Dict
import flet
from flet import Page, Text, ElevatedButton, Column, Row, Container, Card, SnackBar


EASY_QUESTIONS = [
    {
        "question": "Якого кольору небо у ясний день?",
        "options": {"A": "Зелене", "B": "Синє", "C": "Червоне", "D": "Жовте"},
        "answer": "B",
    },
    {
        "question": "Скільки днів у тижні?",
        "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
        "answer": "C",
    },
    {
        "question": "Столиця Франції?",
        "options": {"A": "Берлін", "B": "Париж", "C": "Рим", "D": "Мадрид"},
        "answer": "B",
    },
    {
        "question": "Хто автор твору 'Кобзар'?",
        "options": {"A": "Іван Франко", "B": "Леся Українка", "C": "Тарас Шевченко", "D": "Михайло Коцюбинський"},
        "answer": "C",
    },
    {
        "question": "Яка планета названа на честь римського бога війни?",
        "options": {"A": "Марс", "B": "Юпітер", "C": "Венера", "D": "Сатурн"},
        "answer": "A",
    },
]

MEDIUM_QUESTIONS = [
    {
        "question": "Скільки материків існує на Землі?",
        "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
        "answer": "C",
    },
    {
        "question": "Хто написав музику до гімну України?",
        "options": {"A": "Михайло Вербицький", "B": "Павло Чубинський", "C": "Микола Лисенко", "D": "Шопен"},
        "answer": "A",
    },
    {
        "question": "Яка ріка є найдовшою в Україні?",
        "options": {"A": "Дніпро", "B": "Дністер", "C": "Південний Буг", "D": "Дунай"},
        "answer": "A",
    },
    {
        "question": "Який океан є найбільшим за площею?",
        "options": {"A": "Атлантичний", "B": "Індійський", "C": "Тихий", "D": "Північний Льодовитий"},
        "answer": "C",
    },
    {
        "question": "Яка країна винайшла порох?",
        "options": {"A": "Японія", "B": "Китай", "C": "Індія", "D": "Англія"},
        "answer": "B",
    },
]

HARD_QUESTIONS = [
    {
        "question": "Хто відкрив Америку у 1492 році?",
        "options": {"A": "Фернан Магеллан", "B": "Васко да Гама", "C": "Христофор Колумб", "D": "Джеймс Кук"},
        "answer": "C",
    },
    {
        "question": "Хімічний символ золота?",
        "options": {"A": "Ag", "B": "Au", "C": "Fe", "D": "Zn"},
        "answer": "B",
    },
    {
        "question": "Який український літературний твір починається словами 'Реве та стогне Дніпр широкий'?",
        "options": {"A": "Мойсей", "B": "Енеїда", "C": "Заповіт", "D": "Причинна"},
        "answer": "D",
    },
    {
        "question": "Хто є автором теорії відносності?",
        "options": {"A": "Ньютон", "B": "Ейнштейн", "C": "Галілей", "D": "Коперник"},
        "answer": "B",
    },
    {
        "question": "У якому році Україна проголосила незалежність?",
        "options": {"A": "1989", "B": "1990", "C": "1991", "D": "1992"},
        "answer": "C",
    },
]

QUESTIONS = EASY_QUESTIONS + MEDIUM_QUESTIONS + HARD_QUESTIONS


PRIZE_LADDER = [
    100, 200, 300, 500, 1000,      
    2000, 4000, 8000, 16000, 32000, 
    64000, 125000, 250000, 500000, 1000000 
]


SAVE_FILE = "millionaire_save.json"

def save_game(state: Dict):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state
    except Exception:
        return None

def generate_audience_poll(correct: str, options: List[str]) -> Dict[str, int]:
    """Проста генерація відсотків залу.
    Правильний варіант отримує більше голосів."""
    # Відсотки прості, сума 100
    base = {o: 0 for o in options}
    # Правильний отримує 50..70%
    correct_pct = random.randint(50, 70)
    base[correct] = correct_pct
    remaining = 100 - correct_pct
    wrongs = [o for o in options if o != correct]
    # Розподілимо залишок порівну з невеликим випадковим шумом
    for i, w in enumerate(wrongs):
        if i == len(wrongs) - 1:
            base[w] = remaining
        else:
            x = random.randint(0, remaining)
            base[w] = x
            remaining -= x
    return base

def phone_a_friend_suggestion(correct: str, options: List[str]) -> str:
    """Дзвінок другу: друг іноді помиляється.
    Існує 70% шанс, що друг скаже правильну відповідь."""
    if random.randint(1, 100) <= 70:
        return correct
    else:
        wrongs = [o for o in options if o != correct]
        return random.choice(wrongs)


def main(page: Page):
    page.title = "Хто хоче стати мільйонером?"
    page.horizontal_alignment = "center"
    page.window_width = 800
    page.window_height = 600

    current_index = 0
    used_5050 = False
    used_phone = False
    used_audience = False
    removed_options = []
    correct_count = 0

    saved_state = load_game()
    if saved_state:
        current_index = saved_state.get("current_index", 0)
        used_5050 = saved_state.get("used_5050", False)
        used_phone = saved_state.get("used_phone", False)
        used_audience = saved_state.get("used_audience", False)
        removed_options = saved_state.get("removed_options", [])
        correct_count = saved_state.get("correct_count", 0)
        
    question_text = Text("", size=18, weight="bold", selectable=True)
    prize_text = Text("Гроші: 0", size=16)
    info_text = Text("", size=14)
    option_buttons = {}
    restart_button = ElevatedButton("Почати заново", visible=False, on_click=lambda e: restart_game())

    page.snack_bar = SnackBar(Text("", size=14), open=False)

    def show_snack(msg: str):
        page.snack_bar.content = Text(msg, size=14)
        page.snack_bar.open = True
        info_text.value = msg
        page.update()
        
    def save_state():
        state = {
            "current_index": current_index,
            "used_5050": used_5050,
            "used_phone": used_phone,
            "used_audience": used_audience,
            "removed_options": removed_options,
            "correct_count": correct_count,
        }
        save_game(state)

    def load_question():
        nonlocal current_index, removed_options
        removed_options = []
        if current_index >= len(QUESTIONS):
            show_snack("Вітаю! Ви відповіли на всі питання!")
            restart_button.visible = True
            page.update()
            return
        q = QUESTIONS[current_index]
        question_text.value = f"Питання {current_index + 1}: {q['question']}"
        prize_text.value = f"Гроші: {PRIZE_LADDER[current_index]} грн"
        for k, btn in option_buttons.items():
            btn.text = f"{k}: {q['options'][k]}"
            btn.disabled = False
            btn.visible = True
        restart_button.visible = False
        info_text.value = ""
        page.update()

    def answer_click(letter: str):
        nonlocal current_index, correct_count
        q = QUESTIONS[current_index]
        if letter == q["answer"]:
            correct_count += 1
            show_snack("Правильно!")
            current_index += 1
            save_state()
            if current_index >= len(QUESTIONS):
                prize_text.value = f"Гроші: {PRIZE_LADDER[-1]} грн"
                question_text.value = "Ви виграли всі призи! Вітаю!"
                for btn in option_buttons.values():
                    btn.disabled = True
                restart_button.visible = True
                save_state()
                page.update()
                return
            load_question()
        else:
            show_snack(f"Невірно. Правильна відповідь: {q['answer']}.")
            final = 0
            if correct_count >= 10:
                final = PRIZE_LADDER[9]
            elif correct_count >= 5:
                final = PRIZE_LADDER[4]
            question_text.value = f"Гра завершена. Ви заробили {final} грн."
            for btn in option_buttons.values():
                btn.disabled = True
            restart_button.visible = True
            page.update()

    def use_5050(e):
        nonlocal used_5050, removed_options
        if used_5050:
            show_snack("50/50 вже використана.")
            return
        q = QUESTIONS[current_index]
        correct = q["answer"]
        wrongs = [o for o in q["options"].keys() if o != correct]
        removed_options = random.sample(wrongs, 2)
        for r in removed_options:
            option_buttons[r].visible = False
        used_5050 = True
        save_state()
        page.update()

    def use_phone(e):
        nonlocal used_phone
        if used_phone:
            show_snack("Дзвінок другу вже використано.")
            return
        q = QUESTIONS[current_index]
        suggestion = phone_a_friend_suggestion(q["answer"], list(q["options"].keys()))
        show_snack(f"Друг думає, що правильна відповідь: {suggestion}")
        used_phone = True
        save_state()

    def use_audience(e):
        nonlocal used_audience
        if used_audience:
            show_snack("Допомога залу вже використана.")
            return
        q = QUESTIONS[current_index]
        poll = generate_audience_poll(q["answer"], list(q["options"].keys()))
        s = "Голоси залу:\n"
        for k in q["options"].keys():
            s += f"{k}: {poll[k]}%  "
        show_snack(s)
        used_audience = True
        save_state()

    def make_option_button(letter: str):
        def on_click(e):
            answer_click(letter)
        return ElevatedButton(text=letter, on_click=on_click, width=320)

    def restart_game():
        nonlocal current_index, used_5050, used_phone, used_audience, removed_options, correct_count
        current_index = 0
        used_5050 = False
        used_phone = False
        used_audience = False
        removed_options = []
        correct_count = 0
        save_state()
        load_question()

    for l in ["A", "B", "C", "D"]:
        option_buttons[l] = make_option_button(l)

    btn_5050 = ElevatedButton("50/50", on_click=use_5050, width=120)
    btn_phone = ElevatedButton("Дзвінок другу", on_click=use_phone, width=160)
    btn_audience = ElevatedButton("Допомога залу", on_click=use_audience, width=140)

    options_col = Column([option_buttons["A"], option_buttons["B"], option_buttons["C"], option_buttons["D"]], spacing=10)
    hints_row = Row([btn_5050, btn_phone, btn_audience], spacing=10)

    page.add(
        Column(
            [
                Card(content=Container(question_text, padding=10)),
                Row([prize_text], alignment="center"),
                Container(options_col, padding=10),
                hints_row,
                info_text,
                restart_button,
            ],
            spacing=12,
        )
    )

    load_question()


if __name__ == "__main__":
    flet.app(target=main)
