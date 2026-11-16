"""Effect pickers choose a tool; only their main button runs its command."""
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
                        if action in by_action and not action.isSeparator()}
        self.selected_key = default
        self.setObjectName('effect_group_' + group)
        self.setProperty('effectGroup', True)
        self.setProperty('compact', True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        # The top menu executes commands. These separate choices only select
        # a tool, retaining the source commands' translated labels and icons.
        picker = QMenu(title, self)
        self.choice_actions = {}
        for source in menu.actions():
            if source.isSeparator():
                picker.addSeparator()
                continue
            key = by_action[source]
            choice = QAction(picker)
            choice.setCheckable(True)
            choice.triggered.connect(lambda checked=False, key=key: self.remember(key))
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

    def sync(self, *_):
        # A stereo-only or selection-only choice must not block the rest of its
        # group. Display an available alternative without losing the preference.
        self.current_key = self.selected_key
        available = lambda key: self.window.wave_effect_available(key, require_selection=False)
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
            'Choose a tool with the arrow. Select audio, then click the icon to open or apply it.')))

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
