from textual.app import App


class DummyApp(App):
    CSS_PATH = "print_tui.css"


app = DummyApp()
try:
    print(app.stylesheet.css_errors)
except Exception as e:
    print(e)
