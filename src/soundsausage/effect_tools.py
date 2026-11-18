"""Dialog-effect groups open settings on choice and remember the last dialog."""
from .i18n import Literal, tr, install_language
from .i18n_widgets import QAction, QMenu, QToolButton


class EffectToolButton(QToolButton):
    def __init__(self, window, group, title, menu, default, parent=None):
        super().__init__(parent)
        self.window = window
        self.group = group
        self.title = title
        self.default_key = default
        by_action = {action: key for key, action in window.actions.items()}
        self.effects = {by_action[action]: action for action in menu.actions()
                        if action in by_action and not action.isSeparator()
                        and by_action[action] not in window.DIRECT_EFFECT_ACTIONS}
        self.selected_key = default
        self.setObjectName('effect_group_' + group)
        self.setProperty('effectGroup', True)
        self.setProperty('compact', True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        # Keep immediate operations out of these groups. Choosing an entry
        # opens its dialog through the guarded source command exactly once.
        picker = QMenu(title, self)
        self.choice_actions = {}
        separator = False
        for source in menu.actions():
            if source.isSeparator():
                separator = True
                continue
            key = by_action[source]
            if key not in self.effects:
                continue
            if separator and self.choice_actions:
                picker.addSeparator()
            separator = False
            choice = QAction(picker)
            choice.setCheckable(True)
            choice.triggered.connect(lambda checked=False, key=key: self.choose(key))
            picker.addAction(choice)
            self.choice_actions[key] = choice
        self.setMenu(picker)
        self.clicked.connect(self.run)
        for key, action in self.effects.items():
            action.changed.connect(self.sync)
            action.triggered.connect(lambda checked=False, key=key: self.remember(key))
        install_language().changed.connect(self.sync)
        self.restore()

    def remember(self, key):
        self.selected_key = key
        self.sync()

    def choose(self, key):
        if not self.window.wave_effect_available(key):
            return
        self.remember(key)
        self.run()

    def sync(self, *_):
        # A stereo-only or selection-only choice must not block the rest of its
        # group. Display an available alternative without losing the preference.
        self.current_key = self.selected_key
        available = self.window.wave_effect_available
        if not available(self.current_key):
            self.current_key = next((key for key, action in self.effects.items()
                                     if available(key)), self.selected_key)
        action = self.effects[self.current_key]
        self.setEnabled(any(available(key) for key in self.effects))
        for key, source in self.effects.items():
            choice = self.choice_actions[key]
            choice.setText(Literal(source.text()))
            choice.setIcon(source.icon())
            choice.setEnabled(available(key))
            choice.setVisible(source.isVisible())
            choice.setChecked(key == self.current_key)
            choice.setToolTip(Literal(source.toolTip()))
        label = action.text().replace('&', '')
        title = tr(self.title).replace('&', '')
        self.setText(Literal(label))
        self.setIcon(action.icon())
        self.setAccessibleName(Literal(title + ': ' + label))
        self.setToolTip(Literal(title + ': ' + label + '\n' + tr(
            'Choose an effect to open its settings; click the icon to reopen the last effect.')))

    def run(self):
        action = self.effects[self.current_key]
        if self.isEnabled() and self.window.require_effect_selection() and action.isEnabled():
            action.trigger()

    def restore(self):
        key = self.window.ui_settings.value('ui/effect_tools/' + self.group, self.default_key)
        self.selected_key = key if isinstance(key, str) and key in self.effects else self.default_key
        self.sync()

    def save(self):
        self.window.ui_settings.setValue('ui/effect_tools/' + self.group, self.selected_key)
