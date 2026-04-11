import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from database import progress_manager


# Colors
C_BG = (0.07, 0.09, 0.15, 1)
C_CARD = (0.13, 0.16, 0.24, 1)
C_GREEN = (0.20, 0.78, 0.35, 1)
C_RED = (0.92, 0.25, 0.20, 1)
C_BLUE = (0.12, 0.56, 0.97, 1)
C_YELLOW = (1.0, 0.80, 0.10, 1)
C_TEXT = (1, 1, 1, 1)
C_SUBTEXT = (0.75, 0.80, 0.90, 1)


def _round_btn(text, color, text_color=(1, 1, 1, 1), font_size=16):
    btn = Button(
        text=text,
        background_normal='',
        background_color=(0, 0, 0, 0),
        color=text_color,
        font_size=dp(font_size),
        bold=True,
        size_hint_y=None,
        height=dp(54),
    )
    with btn.canvas.before:
        c = Color(*color)
        rr = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(12)])
    btn.bind(pos=lambda *a: setattr(rr, 'pos', btn.pos))
    btn.bind(size=lambda *a: setattr(rr, 'size', btn.size))
    return btn


class LessonScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lesson = None
        self.exercises = []
        self.current_index = 0
        self.score = 0
        self.answered = False

    def load_lesson(self, lesson):
        self.lesson = lesson
        self.exercises = lesson['exercises']
        self.current_index = 0
        self.score = 0
        self.answered = False
        self._render()

    def _render(self):
        self.clear_widgets()
        if self.current_index >= len(self.exercises):
            self._show_result()
            return

        exercise = self.exercises[self.current_index]
        root = BoxLayout(orientation='vertical', padding=[dp(16), dp(16), dp(16), dp(16)], spacing=dp(12))

        with self.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self._bg, 'pos', self.pos))
        self.bind(size=lambda *a: setattr(self._bg, 'size', self.size))

        # Progress bar row
        progress_row = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(10))
        back_btn = Button(
            text="✕",
            font_size=dp(18),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.7, 0.7, 0.8, 1),
            size_hint_x=None,
            width=dp(36),
        )
        back_btn.bind(on_release=lambda *a: self._quit_lesson())

        pbar = ProgressBar(
            max=len(self.exercises),
            value=self.current_index,
        )
        count_label = Label(
            text=f"{self.current_index + 1}/{len(self.exercises)}",
            font_size=dp(12),
            color=C_SUBTEXT,
            size_hint_x=None,
            width=dp(44),
        )
        progress_row.add_widget(back_btn)
        progress_row.add_widget(pbar)
        progress_row.add_widget(count_label)
        root.add_widget(progress_row)

        # Lesson title
        title_label = Label(
            text=self.lesson['title'],
            font_size=dp(14),
            color=C_SUBTEXT,
            size_hint_y=None,
            height=dp(24),
            bold=False,
            halign='center',
        )
        title_label.bind(size=lambda *a: setattr(title_label, 'text_size', title_label.size))
        root.add_widget(title_label)

        ex_type = exercise.get('type')

        if ex_type == 'translate_fr_to_de':
            self._build_translate_input(root, exercise)
        elif ex_type == 'select_de_from_fr':
            self._build_select_exercise(root, exercise)
        else:
            self._build_translate_input(root, exercise)

        self.add_widget(root)
        self._root_layout = root

    def _card_widget(self, content_widget, padding=16):
        wrapper = BoxLayout(size_hint_y=None, height=content_widget.height + dp(padding * 2))
        with wrapper.canvas.before:
            Color(*C_CARD)
            rr = RoundedRectangle(pos=wrapper.pos, size=wrapper.size, radius=[dp(14)])
        wrapper.bind(pos=lambda *a: setattr(rr, 'pos', wrapper.pos))
        wrapper.bind(size=lambda *a: setattr(rr, 'size', wrapper.size))
        wrapper.add_widget(content_widget)
        return wrapper

    def _build_translate_input(self, root, exercise):
        # Instruction
        instr = Label(
            text="Traduisez en allemand :",
            font_size=dp(15),
            color=C_SUBTEXT,
            size_hint_y=None,
            height=dp(28),
            halign='center',
        )
        instr.bind(size=lambda *a: setattr(instr, 'text_size', instr.size))
        root.add_widget(instr)

        # Question card
        q_label = Label(
            text=exercise['question_fr'],
            font_size=dp(34),
            bold=True,
            color=C_TEXT,
            size_hint_y=None,
            height=dp(80),
            halign='center',
        )
        q_label.bind(size=lambda *a: setattr(q_label, 'text_size', q_label.size))

        card = BoxLayout(
            size_hint_y=None,
            height=dp(100),
            padding=[dp(16), dp(10), dp(16), dp(10)],
        )
        with card.canvas.before:
            Color(*C_CARD)
            rr = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda *a: setattr(rr, 'pos', card.pos))
        card.bind(size=lambda *a: setattr(rr, 'size', card.size))
        card.add_widget(q_label)
        root.add_widget(card)

        if exercise.get('hint'):
            hint = Label(
                text=f"💡 {exercise['hint']}",
                font_size=dp(12),
                color=(0.6, 0.7, 0.8, 0.8),
                size_hint_y=None,
                height=dp(24),
                halign='center',
            )
            hint.bind(size=lambda *a: setattr(hint, 'text_size', hint.size))
            root.add_widget(hint)

        root.add_widget(Widget())

        # Text input
        self.text_input = TextInput(
            hint_text="Tapez la traduction en allemand...",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(54),
            multiline=False,
            background_color=(0.15, 0.18, 0.28, 1),
            foreground_color=C_TEXT,
            cursor_color=C_BLUE,
        )
        root.add_widget(self.text_input)

        # Feedback area (hidden initially)
        self.feedback_label = Label(
            text="",
            font_size=dp(15),
            size_hint_y=None,
            height=dp(36),
            halign='center',
        )
        self.feedback_label.bind(size=lambda *a: setattr(self.feedback_label, 'text_size', self.feedback_label.size))
        root.add_widget(self.feedback_label)

        # Submit / Continue button
        self.action_btn = _round_btn("Vérifier", C_BLUE)
        self.action_btn.bind(on_release=lambda *a: self._check_translate(exercise))
        root.add_widget(self.action_btn)

    def _check_translate(self, exercise):
        if self.answered:
            self._next_exercise()
            return

        user = self.text_input.text.strip().lower()
        correct = exercise['answer_de'].lower()

        if user == correct:
            self.score += 1
            self.feedback_label.text = f"✅ Correct !  →  {exercise['answer_de']}"
            self.feedback_label.color = C_GREEN
        else:
            self.feedback_label.text = f"❌ Réponse : {exercise['answer_de']}"
            self.feedback_label.color = C_RED

        self.answered = True
        self.action_btn.text = "Continuer →"

    def _build_select_exercise(self, root, exercise):
        # Instruction
        instr = Label(
            text="Choisissez la bonne traduction :",
            font_size=dp(15),
            color=C_SUBTEXT,
            size_hint_y=None,
            height=dp(28),
            halign='center',
        )
        instr.bind(size=lambda *a: setattr(instr, 'text_size', instr.size))
        root.add_widget(instr)

        # Question card
        q_label = Label(
            text=exercise['question_fr'],
            font_size=dp(32),
            bold=True,
            color=C_TEXT,
            size_hint_y=None,
            height=dp(80),
            halign='center',
        )
        q_label.bind(size=lambda *a: setattr(q_label, 'text_size', q_label.size))

        card = BoxLayout(
            size_hint_y=None,
            height=dp(100),
            padding=[dp(16), dp(10), dp(16), dp(10)],
        )
        with card.canvas.before:
            Color(*C_CARD)
            rr = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda *a: setattr(rr, 'pos', card.pos))
        card.bind(size=lambda *a: setattr(rr, 'size', card.size))
        card.add_widget(q_label)
        root.add_widget(card)
        root.add_widget(Widget(size_hint_y=None, height=dp(10)))

        # Options grid
        options_grid = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(130),
        )
        self.option_buttons = []
        for opt in exercise['options']:
            btn = Button(
                text=opt,
                font_size=dp(16),
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=C_TEXT,
                size_hint_y=None,
                height=dp(60),
            )
            with btn.canvas.before:
                c_ref = Color(*C_CARD)
                rr = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[dp(10)])
            btn.bind(pos=lambda *a, r=rr: setattr(r, 'pos', a[0].pos))
            btn.bind(size=lambda *a, r=rr: setattr(r, 'size', a[0].size))
            btn.bind(on_release=lambda b, o=opt, e=exercise, c=c_ref: self._check_select(b, o, e, c))
            self.option_buttons.append((btn, c_ref))
            options_grid.add_widget(btn)

        root.add_widget(options_grid)
        root.add_widget(Widget())

        self.feedback_label = Label(
            text="",
            font_size=dp(15),
            size_hint_y=None,
            height=dp(36),
            halign='center',
        )
        self.feedback_label.bind(size=lambda *a: setattr(self.feedback_label, 'text_size', self.feedback_label.size))
        root.add_widget(self.feedback_label)

        self.continue_btn = _round_btn("Continuer →", C_BLUE)
        self.continue_btn.opacity = 0
        self.continue_btn.disabled = True
        self.continue_btn.bind(on_release=lambda *a: self._next_exercise())
        root.add_widget(self.continue_btn)

    def _check_select(self, btn, choice, exercise, color_ref):
        if self.answered:
            return
        self.answered = True
        correct = exercise['answer']

        for b, c in self.option_buttons:
            b.disabled = True
            if b.text == correct:
                c.rgba = C_GREEN
            elif b.text == choice and choice != correct:
                c.rgba = C_RED

        if choice == correct:
            self.score += 1
            self.feedback_label.text = f"✅ Correct !"
            self.feedback_label.color = C_GREEN
        else:
            self.feedback_label.text = f"❌ Réponse : {correct}"
            self.feedback_label.color = C_RED

        self.continue_btn.opacity = 1
        self.continue_btn.disabled = False

    def _next_exercise(self):
        self.current_index += 1
        self.answered = False
        self._render()

    def _show_result(self):
        self.clear_widgets()
        total = len(self.exercises)
        score_pct = int((self.score / total) * 100) if total > 0 else 0
        xp_earned = int(self.lesson['xp'] * (score_pct / 100))

        progress_manager.complete_lesson(self.lesson['id'], xp_earned, score_pct)

        root = BoxLayout(
            orientation='vertical',
            padding=[dp(30), dp(60), dp(30), dp(40)],
            spacing=dp(20),
        )
        with self.canvas.before:
            Color(*C_BG)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=lambda *a: setattr(self._bg, 'pos', self.pos))
        self.bind(size=lambda *a: setattr(self._bg, 'size', self.size))

        emoji = "🏆" if score_pct >= 80 else ("👍" if score_pct >= 50 else "📚")
        result_emoji = Label(text=emoji, font_size=dp(64), size_hint_y=None, height=dp(80))
        root.add_widget(result_emoji)

        result_title = Label(
            text="Leçon terminée !",
            font_size=dp(26),
            bold=True,
            color=C_TEXT,
            size_hint_y=None,
            height=dp(40),
            halign='center',
        )
        result_title.bind(size=lambda *a: setattr(result_title, 'text_size', result_title.size))
        root.add_widget(result_title)

        score_label = Label(
            text=f"{self.score} / {total} correct",
            font_size=dp(20),
            color=C_SUBTEXT,
            size_hint_y=None,
            height=dp(34),
            halign='center',
        )
        score_label.bind(size=lambda *a: setattr(score_label, 'text_size', score_label.size))
        root.add_widget(score_label)

        xp_label = Label(
            text=f"⚡ +{xp_earned} XP",
            font_size=dp(28),
            bold=True,
            color=C_YELLOW,
            size_hint_y=None,
            height=dp(44),
            halign='center',
        )
        xp_label.bind(size=lambda *a: setattr(xp_label, 'text_size', xp_label.size))
        root.add_widget(xp_label)

        root.add_widget(Widget())

        home_btn = _round_btn("Retour aux leçons", C_BLUE, font_size=17)
        home_btn.bind(on_release=lambda *a: self._go_home())
        root.add_widget(home_btn)

        if score_pct < 100:
            retry_btn = _round_btn("Recommencer", (0.25, 0.28, 0.38, 1), font_size=15)
            retry_btn.bind(on_release=lambda *a: self.load_lesson(self.lesson))
            root.add_widget(retry_btn)

        self.add_widget(root)

    def _go_home(self):
        self.manager.current = 'home'

    def _quit_lesson(self):
        self.manager.current = 'home'
