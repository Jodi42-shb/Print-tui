from textual.app import App


class DummyApp(App):
    CSS_PATH = "print_tui.css"


app = DummyApp()
app.stylesheet.read()

errors = app.stylesheet.css_errors
if errors:
    for e in errors:
        print(e)
else:
    print("NO ERRORS FOUND")
