# SPDX-License-Identifier: Apache-2.0
"""The app's two looks: "adwaita" (GNOME style, default) and "classic" (MousePods 1.0/1.1), switched in
Settings > Appearance, plus the new overview and sidebar of the GNOME look.

Run:  python -m unittest tests.test_ui_look -v
"""
import json
import os
import re
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


HTML = read("ui", "index.html")


def sheet(name):
    m = re.search(r'<style id="skin-%s">(.*?)</style>' % name, HTML, re.S)
    assert m, name
    return m.group(1)


class LookTests(unittest.TestCase):
    def test_two_sheets_and_the_boot_script(self):
        classic, adw = sheet("classic"), sheet("adw")
        self.assertIn(".adw-only{display:none!important}", classic)
        self.assertIn(".classic-only{display:none!important}", adw)
        boot = HTML[HTML.index('<script id="look-boot">'):]
        boot = boot[:boot.index("</script>")]
        self.assertIn('let s="adwaita"', boot)                       # the new look is the default
        self.assertIn('getElementById("skin-classic").disabled=s==="adwaita"', boot)
        self.assertLess(HTML.index('<script id="look-boot">'), HTML.index("</head>"))   # before the first paint

    def test_adwaita_sheet_defines_what_the_canvases_read(self):
        adw = sheet("adw")
        used = set(re.findall(r'cv\("(--[a-z0-9-]+)"\)', HTML))
        self.assertTrue(used)
        for var in used:
            self.assertIn(var + ":", adw, var)

    def test_dark_colors_follow_the_system_or_the_setting(self):
        adw = sheet("adw")
        self.assertIn(":root:not([data-theme=light])", adw)
        self.assertIn(":root[data-theme=dark]", adw)

    def test_settings_switches(self):
        for key, values in (("ui_skin", ("adwaita", "classic")), ("ui_scheme", ("system", "light", "dark"))):
            m = re.search(r'<div class="seg" data-key="%s">(.*?)</div>' % key, HTML, re.S)
            self.assertIsNotNone(m, key)
            self.assertEqual(tuple(re.findall(r'data-v="(\w+)"', m.group(1))), values)
        import airpods_mouse_controller as m
        self.assertEqual(m.DEFAULTS["ui_skin"], "adwaita")
        self.assertEqual(m.DEFAULTS["ui_scheme"], "system")

    def test_sidebar_main_pages_then_advanced(self):
        nav = HTML[HTML.index('<nav id="nav"'):HTML.index("</nav>")]
        adv = nav[nav.index('<div class="nav-adv"'):]
        main = nav[:nav.index('<div class="nav-adv"')]
        self.assertEqual(re.findall(r'data-p="(\w+)"', main), ["overview", "games", "sims", "calib", "settings"])
        self.assertEqual(sorted(re.findall(r'data-p="(\w+)"', adv)),
                         sorted(["motion", "gestures", "labo", "sensors", "device", "garmin", "log", "about"]))
        # the classic look keeps its own order
        classic = sheet("classic")
        order = [p for p, _ in sorted(re.findall(r"nav a\[data-p=(\w+)\]\{order:(\d+)\}", classic), key=lambda x: int(x[1]))]
        self.assertEqual(order, ["overview", "motion", "settings", "calib", "gestures", "labo", "sims", "games",
                                 "garmin", "sensors", "device", "log", "about"])

    def test_every_page_is_reachable(self):
        pages = set(re.findall(r'<section class="page[^"]*" id="p-(\w+)"', HTML))
        linked = set(re.findall(r'data-p="(\w+)"', HTML)) | {"welcome", "news"}
        self.assertEqual(pages - linked, set())

    def test_new_texts_are_translated(self):
        keys = set(re.findall(r'(?:data-i18n(?:-html)?="|t\(")(v2\.[a-z0-9_.]+)', HTML))
        self.assertTrue(keys)
        for code in ("en", "fr", "de"):
            strings = json.loads(read("ui", "i18n", code + ".json"))
            self.assertEqual(sorted(k for k in keys if k not in strings), [], code)

    def test_overview_reuses_the_live_controls(self):
        ov = HTML[HTML.index('<section class="page on" id="p-overview">'):]
        ov = ov[:ov.index("</section>\n\n")] if "</section>\n\n" in ov else ov
        self.assertIn('data-key="mode"', ov)
        self.assertIn('data-key="source"', ov)
        self.assertIn('data-k="souris.px_per_deg"', ov)
        self.assertIn("#p-overview input[data-k]", HTML)       # filled and saved like the Settings page


class PoseInStreamTests(unittest.TestCase):
    def _ui(self, opentrack):
        import mousepods_web as w
        ui = w.WebUI.__new__(w.WebUI)
        ui.ctl = types.SimpleNamespace(opentrack=opentrack)
        return ui

    def test_no_angles_without_the_simulator_outputs(self):
        self.assertIsNone(self._ui(None)._pose())

    def test_angles_when_computed(self):
        ot = types.SimpleNamespace(pose=[0.0, 0.0, 0.0, 12.44, -3.81, 1.06])
        self.assertEqual(self._ui(ot)._pose(), [12.4, -3.8, 1.1])


if __name__ == "__main__":
    unittest.main()
