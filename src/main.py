# -*- coding: utf-8 -*-

"""
This file is part of the Mini Format Pack add-on for Anki.

Main Module, hooks add-on methods into Anki.

Copyright: (c) 2014-2018 Stefan van den Akker <neftas@protonmail.com>
           (c) 2017-2018 Damien Elmes <http://ichi2.net/contact.html>
           (c) 2018 Glutanimate <https://glutanimate.com/>
License: GNU AGPLv3 <https://www.gnu.org/licenses/agpl.html>
"""

import html
from aqt import mw
from aqt.qt import *
from aqt.utils import getOnlyText
from anki.hooks import addHook
from anki.lang import _
from anki.utils import isWin, isMac
from aqt.gui_hooks import (
    profile_did_open,
    profile_will_close,

    editor_did_init_shortcuts,
    editor_did_init_buttons,
    editor_will_show_context_menu,
)
from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import (
    QCursor,
    QIcon,
    QKeySequence,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QMenu,
    QShortcut,
)


from .consts import addon_path

# Config

def getConfig():
    return mw.addonManager.getConfig(__name__)


# Format Functions

def insertOrderedList(editor):
    editor.web.eval("setFormat('insertOrderedList')")


def insertUnorderedList(editor):
    editor.web.eval("setFormat('insertUnorderedList')")


def strikeThrough(editor):
    editor.web.eval("setFormat('strikeThrough')")


def indent(editor):
    editor.web.eval("setFormat('indent')")


def insertTab(editor):
    editor.web.eval("setFormat('inserthtml', '&emsp;')")


def outdent(editor):
    editor.web.eval("setFormat('outdent')")


def formatAbbr(editor):
    text = html.escape(getOnlyText(_("Full name:"), default=""))
    if not text:
        return
    editor.web.eval("""wrap("<abbr title='{}'>", "</abbr>")""".format(text))


def formatBlockPre(editor):
    editor.web.eval("setFormat('formatBlock', 'pre')")


def formatCode(editor):
    editor.web.eval("wrap('<code><font color=\"#000\">', '</font></code>')")


def formatCodeComment(editor):
    editor.web.eval(
        "wrap('<code><font color=\"#95a5a6\"><i>//', '</i></font></code>')")


def formatCodeKeyword(editor):
    editor.web.eval(
        "wrap('<code><font color=\"#234e99\"><b>', '</b></font></code>')")


def formatCodeKeywordLite(editor):
    editor.web.eval("wrap('<code><font color=\"#289\">', '</font></code>')")


def formatCodeKeywordLiteBold(editor):
    editor.web.eval(
        "wrap('<code><font color=\"#289\"><b>', '</b></font></code>')")


def formatCodeNumber(editor):
    editor.web.eval("wrap('<code><font color=\"#99234e\">', '</font></code>')")


def formatCodeQuotedString(editor):
    editor.web.eval(
        "wrap('<code><font color=\"#23996d\">\"', '\"</font></code>')")


def formatCodeString(editor):
    editor.web.eval("wrap('<code><font color=\"#23996d\">', '</font></code>')")


def formatKeyboard(editor):
    editor.web.eval("wrap('<kbd>', '</kbd>')")


def fontBigger(editor):
    modifiers = QApplication.keyboardModifiers()
    if (modifiers & Qt.ShiftModifier):
        editor.web.eval(
            "wrap('<span style=\"font-size: 1.2em\">', '</span><br>')")
    else:
        editor.web.eval(
            "wrap('<span style=\"font-size: 1.2em\">', '</span>')")


def fontSmaller(editor):
    modifiers = QApplication.keyboardModifiers()
    if (modifiers & Qt.ShiftModifier):
        editor.web.eval(
            "wrap('<span style=\"font-size: 0.8em\">', '</span><br>')")
    else:
        editor.web.eval("wrap('<span style=\"font-size: 0.8em\">', '</span>')")


def insertHorizontalRule(editor):
    editor.web.eval("setFormat('insertHorizontalRule')")

def insertPipeSeparator(editor):
    editor.web.eval("wrap('', ' | ')")


def justifyCenter(editor):
    editor.web.eval("setFormat('justifyCenter');")


def justifyLeft(editor):
    editor.web.eval("setFormat('justifyLeft');")


def justifyRight(editor):
    editor.web.eval("setFormat('justifyRight');")


def justifyFull(editor):
    editor.web.eval("setFormat('justifyFull');")

def mainPoint(editor):
    editor.web.eval("wrap('<div class=\"main-point\"><span class=\"main-point\">', '</span></div>')")

def resetColorsToInherit(editor):
    editor.web.eval("setFormat('forecolor', '#000');")
    _wrapWithBgColour(editor, 'inherit')

def secondaryPoint(editor):
    editor.web.eval("wrap('<div class=\"secondary-point\"><span class=\"secondary-point\">', '</span></div>')")

# Special format functions

# Background colour
######################################################################

def _updateBackgroundButton(editor):
    editor.web.eval(
        """$("#backcolor")[0].style.backgroundColor = '%s'""" % editor.bcolour)

def onBackground(editor):
    _wrapWithBgColour(editor, editor.bcolour)

def onBgColourChanged(editor):
    _updateBackgroundButton(editor)
    editor.mw.pm.profile['lastBgColor'] = editor.bcolour

def onChangeBgCol(editor):
    new = QColorDialog.getColor(QColor(editor.bcolour), None)
    # native dialog doesn't refocus us for some reason
    editor.parentWindow.activateWindow()
    if new.isValid():
        editor.bcolour = new.name()
        onBgColourChanged(editor)
        _wrapWithBgColour(editor, editor.bcolour)

def setupBackgroundButton(editor):
    editor.bcolour = editor.mw.pm.profile.get("lastBgColor", "#00f")
    onBgColourChanged(editor)


def _wrapWithBgColour(editor, color):
    # On Linux, the standard 'hiliteColor' method works. On Windows and OSX
    # the formatting seems to get filtered out
    editor.web.eval("""
        if (!setFormat('hiliteColor', '%s')) {
            setFormat('backcolor', '%s');
        }
        """ % (color, color))

    if isWin or isMac:
        # remove all Apple style classes, which is needed for
        # text highlighting on platforms other than Linux
        editor.web.eval("""
            var matches = document.querySelectorAll(".Apple-style-span");
            for (var i = 0; i < matches.length; i++) {
                matches[i].removeAttribute("class");
            }
        """)


# UI element creation
######################################################################

def createCustomButton(editor, name, tooltip, hotkey, method):
    if name == "onBackground":
        editor._links[name] = method
        QShortcut(QKeySequence(hotkey), editor.widget,
                  activated=lambda s=editor: method(s))
        return '''<button tabindex=-1 class=linkb title="{}"
                    type="button" onclick="pycmd('{}');return false;">
                    <div id=backcolor style="display:inline-block; background: #000;border-radius: 5px;"
                    class=topbut></div></button>'''.format("{} ({})".format(tooltip, hotkey), name)
    return ""


# Hooks
######################################################################

def onLoadNote(editor):
    setupBackgroundButton(editor)


def show_more_options(editor):
    pos = QCursor.pos()
    pos.setX(pos.x() - 25)
    pos.setY(pos.y() + 15)
    submenu.exec_(pos)


def setup_more_shortcuts(editor):
    submenu_items = getConfig().get("sub-menu", None)
    global submenu
    submenu = QMenu(editor.mw)
    submenu.hide()
    for action in submenu_items:
        try:
            name = action["name"]
            tooltip = action["tooltip"]
            hotkey = action["hotkey"]
        except KeyError:
            print("Simple Format Pack sub-menu: Action not configured properly:", action)
            continue
        icon = QIcon(os.path.join(addon_path, "icons", "{}.png".format(name)))
        a = submenu.addAction(icon, "{} ({})".format(tooltip, hotkey))
        a.setShortcut = hotkey
        a.triggered.connect(lambda _, n=name, e=editor: globals().get(n)(e))
        QShortcut(QKeySequence(hotkey), editor.parentWindow,
                  activated=lambda n=name, e=editor: globals().get(n)(e))


def onSetupButtons(buttons, editor):
    """Add buttons to Editor for Anki 2.1.x"""

    actions = getConfig().get("actions", None)

    setup_more_shortcuts(editor)

    buttons.append(editor.addButton(os.path.join(addon_path, "icons", "more_rotated.png"),
                                    "more formatting options",
                                    show_more_options,
                                    tip="more formatting options"))

    if not actions:
        return buttons

    for action in actions:
        try:
            name = action["name"]
            tooltip = action["tooltip"]
            label = action.get("label", "")
            hotkey = action["hotkey"]
            method = globals().get(name)
        except KeyError:
            print("Simple Format Pack: Action not configured properly:", action)
            continue

        icon_path = os.path.join(addon_path, "icons", "{}.png".format(name))
        if not os.path.exists(icon_path):
            icon_path = ""

        if action.get("custom", False):
            b = createCustomButton(editor, name, tooltip, hotkey, method)
        else:
            b = editor.addButton(icon_path, name, method,
                                 tip="{} ({})".format(tooltip, hotkey),
                                 label="" if icon_path else label,
                                 keys=hotkey)
        buttons.append(b)

    return buttons

def on_setup_editor_context_menu(view, menu):
    a = menu.addAction('edit HTML')
    a.triggered.connect(lambda _, e=view.editor: e.onHtmlEdit())
    return


addHook("loadNote", onLoadNote)
addHook("setupEditorButtons", onSetupButtons)
addHook("EditorWebView.contextMenuEvent", on_setup_editor_context_menu)
