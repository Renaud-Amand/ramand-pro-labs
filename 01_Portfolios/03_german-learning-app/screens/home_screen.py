import json
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from database import progress_manager


LESSONS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'lessons.json')
CATEGORY_COLORS = {
    "routier": (0.12, 0.56, 0.97, 1),
    "entreprise": (0.20, 0.78, 0.35, 1),
}
CATEGORY_DONE_COLORS = {
    "routier": (0.08, 0.40, 0.72, 1),
    "entreprise": (0.14, 0.58, 0.26, 1),
}


def load_lessons():
    with open(LESSONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['lessons']


class LessonCard(Button):
    def __init__(self, lesson, completed, score, **kwargs):
        super().__init__(**kwargs)
        self.lesson = lesson
        self.text = ""
        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)
        self.size_hint_y = None
        self.height = dp(100)

        color = CATEGORY_DONE_COLORS.get(lesson['category']) if completed else CATEGORY_COLORS.get(lesson['category'], (0.5, 0.5, 0.5, 1))

        with self.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])

        self.bind(pos=self._update_rect, size=self._update_rect)

        inner = BoxLayout(orientation='horizontal', padding=dp(14), spacing=dp(10))
        inner.size_hint = (1, 1)

        icon_label = Label(
            text=lesson['icon'],
            font_size=dp(32),
            size_hint_x=None,
            width=dp(56),
        )

        info_col = BoxLayout(orientation='vertical', spacing=dp(2))
        title_label = Label(
            text=lesson['title'],
            font_size=dp(17),
            bold=True,
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle',
            text_size=(None, None),
        )
        sub_label = Label(
            text=lesson['subtitle'],
            font_size=dp(12),
            color=(0.9, 0.9, 0.9, 0.85),
            halign='left',
            valign='middle',
        )
        info_col.add_widget(title_label)
        info_col.add_widget(sub_label)

        xp_col = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(64), spacing=dp(2))
        xp_label = Label(
            text=f"{lesson['xp']} XP",
            font_size=dp(14),
            bold=True,
            color=(1, 1, 0.5, 1),
            halign='center',
        )
        if completed:
            status_label = Label(
                text=f"✓ {score}%",
                font_size=dp(12),
                color=(0.8, 1, 0.8, 1),
                halign='center',
            )
        else:
            status_label = Label(
                text="À faire",
                font_size=dp(11),
                color=(1, 1, 1, 0.7),
                halign='center',
            )
        xp_col.add_widget(xp_label)
        xp_col.add_widget(status_label)

        inner.add_widget(icon_label)
        inner.add_widget(info_col)
        inner.add_widget(xp_col)
        self.add_widget(inner)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        root = BoxLayout(orientation='vertical')

        # Header
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110),
            padding=[dp(20), dp(20), dp(20), dp(10)],
        )
        with header.canvas.before:
            Color(0.10, 0.12, 0.20, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[0, 0, dp(20), dp(20)])
        header.bind(pos=lambda *a: setattr(self.header_rect, 'pos', header.pos))
        header.bind(size=lambda *a: setattr(self.header_rect, 'size', header.size))

        progress = progress_manager.get_progress()
        total_xp = progress.get('total_xp', 0)
        streak = progress.get('streak', 0)

        title_label = Label(
            text="🇨🇭 Deutsch Profi",
            font_size=dp(22),
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(34),
            halign='left',
        )
        title_label.bind(size=lambda *a: setattr(title_label, 'text_size', title_label.size))

        stats_label = Label(
            text=f"⚡ {total_xp} XP    🔥 Série: {streak} jour(s)",
            font_size=dp(13),
            color=(0.8, 0.9, 1, 0.9),
            size_hint_y=None,
            height=dp(24),
            halign='left',
        )
        stats_label.bind(size=lambda *a: setattr(stats_label, 'text_size', stats_label.size))

        header.add_widget(title_label)
        header.add_widget(stats_label)

        # Scrollable lesson list
        scroll = ScrollView()
        lesson_list = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            size_hint_y=None,
        )
        lesson_list.bind(minimum_height=lesson_list.setter('height'))

        lessons = load_lessons()

        # Section headers
        current_cat = None
        for lesson in lessons:
            if lesson['category'] != current_cat:
                current_cat = lesson['category']
                cat_label = Label(
                    text=("🚛 Chauffeur Poids Lourds" if current_cat == "routier" else "💼 Entreprise"),
                    font_size=dp(14),
                    bold=True,
                    color=(0.7, 0.8, 1, 0.9),
                    size_hint_y=None,
                    height=dp(30),
                    halign='left',
                )
                cat_label.bind(size=lambda *a, lbl=cat_label: setattr(lbl, 'text_size', lbl.size))
                lesson_list.add_widget(cat_label)

            completed = progress_manager.is_lesson_completed(lesson['id'])
            score = progress_manager.get_lesson_score(lesson['id'])
            card = LessonCard(lesson=lesson, completed=completed, score=score)
            card.bind(on_release=lambda btn, l=lesson: self.start_lesson(l))
            lesson_list.add_widget(card)

        scroll.add_widget(lesson_list)
        root.add_widget(header)
        root.add_widget(scroll)
        self.add_widget(root)

    def start_lesson(self, lesson):
        lesson_screen = self.manager.get_screen('lesson')
        lesson_screen.load_lesson(lesson)
        self.manager.current = 'lesson'

    def on_enter(self):
        self.build_ui()
