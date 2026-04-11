import os
os.environ.setdefault('KIVY_NO_ENV_CONFIG', '1')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from screens.home_screen import HomeScreen
from screens.lesson_screen import LessonScreen

Window.clearcolor = (0.07, 0.09, 0.15, 1)


class DeutschProfiApp(App):
    def build(self):
        self.title = "Deutsch Profi — Allemand Professionnel Suisse"
        Window.size = (420, 750)

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(LessonScreen(name='lesson'))
        return sm


if __name__ == '__main__':
    DeutschProfiApp().run()
