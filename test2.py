from textual.css.stylesheet import Stylesheet

try:
    s = Stylesheet()
    s.read("print_tui.css")
    s.parse()
    if s.css_errors:
        for err in s.css_errors:
            print(f"CSS_ERROR: {err}")
    else:
        print("NO_CSS_ERRORS")
except Exception as e:
    print(f"Exception: {e}")
