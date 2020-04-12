#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for message widgets
"""

from __future__ import print_function, division, absolute_import

from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base, mixin, theme
from tpDcc.libs.qt.widgets import label, avatar, buttons, loading


class MessageTypes(object):
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
    LOADING = 'loading'


@mixin.theme_mixin
@mixin.property_mixin
class BaseMessage(base.BaseWidget, object):
    def __init__(self, text='', parent=None, flags=0):

        self._type = None
        self._text = ''

        super(BaseMessage, self).__init__(parent, flags=flags)

        self.setAttribute(Qt.WA_StyledBackground)

        self.set_show_icon(True)
        self.set_closable(False)
        self.theme_type = MessageTypes.INFO
        self.text = text

    # =================================================================================================================
    # PROPERTIES
    # =================================================================================================================

    def _get_text(self):
        """
        Returns message text
        :return: str
        """

        return self._text

    def _set_text(self, text):
        """
        Sets message text content
        :param text: str
        """

        self._text = str(text)
        self._content_label.setText(self._text)
        self.setVisible(bool(self._text))

    def _get_type(self):
        """
        Returns message type
        :return: float
        """

        return self._type

    def _set_type(self, value):
        """
        Sets message type
        :param value: str
        """

        current_them = self.theme()

        if value in [MessageTypes.INFO, MessageTypes.SUCCESS, MessageTypes.WARNING, MessageTypes.ERROR]:
            self._type = value
        else:
            raise ValueError(
                'Given button type: "{}" is not supported. Supported types '
                'are: info, success, warning, error'.format(value))

        if current_them:
            self._icon_label.image = tp.ResourcesMgr().pixmap(
                self._type, color=getattr(current_them, '{}_color'.format(self._type)))
        else:
            self._icon_label.image = tp.ResourcesMgr().pixmap(self._type)
        self.style().polish(self)

    text = Property(str, _get_text, _set_text)
    theme_type = Property(str, _get_type, _set_type)

    # =================================================================================================================
    # OVERRIDES
    # =================================================================================================================

    def get_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)

        return main_layout

    def ui(self):
        super(BaseMessage, self).ui()

        current_theme = self.theme()

        self._icon_label = avatar.Avatar()
        self._icon_label.theme_size = current_theme.huge if current_theme else theme.Theme.Sizes.HUGE
        self._content_label = label.BaseLabel().secondary()
        self._close_btn = buttons.BaseToolButton().image('close', theme='window').large().icon_only()

        self.main_layout.addWidget(self._icon_label)
        self.main_layout.addWidget(self._content_label)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self._close_btn)

    def setup_signals(self):
        self._close_btn.clicked.connect(partial(self.setVisible, False))

    # =================================================================================================================
    # BASE
    # =================================================================================================================

    def set_closable(self, flag):
        """
        Sets whether or not the message is closable
        :param flag: bool
        """

        self._close_btn.setVisible(flag)

    def set_show_icon(self, flag):
        """
        Sets whether or not the display information type icon is visible or not
        :param flag: bool
        """

        self._icon_label.setVisible(flag)

    def info(self):
        """
        Sets message to info type
        """

        self.theme_type = MessageTypes.INFO

        return self

    def success(self):
        """
        Sets message to success type
        """

        self.theme_type = MessageTypes.SUCCESS

        return self

    def warning(self):
        """
        Sets message to warning type
        """

        self.theme_type = MessageTypes.WARNING

        return self

    def error(self):
        """
        Sets message to error type
        """

        self.theme_type = MessageTypes.ERROR

        return self

    def closable(self):
        """
        Sets message to info type
        """

        self.set_closable(True)

        return self


@mixin.theme_mixin
class PopupMessage(base.BaseWidget, object):
    """
    Message that appears at the top of the window and show s feedback in response to user actions
    """

    DEFAULT_CONFIG = {'duration': 2, 'top': 24}

    closed = Signal()

    def __init__(self, text, duration=None, theme_type=None, closable=False, parent=None):

        self._text = text
        self._duration = duration
        self._theme_type = theme_type
        self._closable = closable

        super(PopupMessage, self).__init__(parent=parent)

        close_timer = QTimer(self)
        close_timer.setSingleShot(True)
        close_timer.timeout.connect(self.close)
        close_timer.timeout.connect(self.closed)
        close_timer.setInterval((duration or self.DEFAULT_CONFIG['duration']) * 1000)
        anim_timer = QTimer(self)
        anim_timer.timeout.connect(self._on_fade_out)
        anim_timer.setInterval((duration or self.DEFAULT_CONFIG['duration']) * 1000 - 300)
        close_timer.start()
        anim_timer.start()

        self._pos_anim = QPropertyAnimation(self)
        self._pos_anim.setTargetObject(self)
        self._pos_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._pos_anim.setDuration(300)
        self._pos_anim.setPropertyName('pos')

        self._opacity_anim = QPropertyAnimation()
        self._opacity_anim.setTargetObject(self)
        self._opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._opacity_anim.setDuration(300)
        self._opacity_anim.setPropertyName('windowOpacity')
        self._opacity_anim.setStartValue(0.0)
        self._opacity_anim.setEndValue(1.0)

        self._set_proper_position(parent)
        self._fade_in()

    # =================================================================================================================
    # OVERRIDES
    # =================================================================================================================

    def get_main_layout(self):
        main_layout = QHBoxLayout()

        return main_layout

    def ui(self):
        super(PopupMessage, self).ui()

        current_theme = self.theme()

        self.setObjectName('message')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WA_TranslucentBackground | Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_StyledBackground)

        if self._theme_type == MessageTypes.LOADING:
            icon_label = loading.CircleLoading.tiny(parent=self)
        else:
            icon_label = avatar.Avatar.tiny()
            current_type = self._theme_type or MessageTypes.INFO
            icon_label.image = tp.ResourcesMgr().pixmap(
                current_type, color=getattr(current_theme, '{}_color'.format(current_type)))

        self._content_label = label.BaseLabel(parent=self)
        self._content_label.setText(self._text)

        self._close_btn = buttons.BaseToolButton(parent=self).image('close', theme='window').icon_only().tiny()
        self._close_btn.setVisible(self._closable or False)

        self.main_layout.addWidget(icon_label)
        self.main_layout.addWidget(self._content_label)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self._close_btn)

    def setup_signals(self):
        self._close_btn.clicked.connect(self.close)

    # =================================================================================================================
    # BASE
    # =================================================================================================================

    @classmethod
    def info(cls, text, parent, duration=None, closable=None):
        """
        Shows an info message
        :param text: str
        :param parent: QWidget
        :param duration: int
        :param closable: bool
        :return: PopupMessage
        """

        popup_message_inst = cls(
            text, theme_type=MessageTypes.INFO, duration=duration, closable=closable, parent=parent)
        popup_message_inst.show()

        return popup_message_inst

    @classmethod
    def success(cls, text, parent, duration=None, closable=None):
        """
        Shows a success message
        :param text: str
        :param parent: QWidget
        :param duration: int
        :param closable: bool
        :return: PopupMessage
        """

        popup_message_inst = cls(
            text, theme_type=MessageTypes.SUCCESS, duration=duration, closable=closable, parent=parent)
        popup_message_inst.show()

        return popup_message_inst

    @classmethod
    def warning(cls, text, parent, duration=None, closable=None):
        """
        Shows a warning message
        :param text: str
        :param parent: QWidget
        :param duration: int
        :param closable: bool
        :return: PopupMessage
        """

        popup_message_inst = cls(
            text, theme_type=MessageTypes.WARNING, duration=duration, closable=closable, parent=parent)
        popup_message_inst.show()

        return popup_message_inst

    @classmethod
    def error(cls, text, parent, duration=None, closable=None):
        """
        Shows an error message
        :param text: str
        :param parent: QWidget
        :param duration: int
        :param closable: bool
        :return: PopupMessage
        """

        popup_message_inst = cls(
            text, theme_type=MessageTypes.ERROR, duration=duration, closable=closable, parent=parent)
        popup_message_inst.show()

        return popup_message_inst

    @classmethod
    def loading(cls, text, parent, duration=None, closable=None):
        """
        Shows a loading message
        :param text: str
        :param parent: QWidget
        :param duration: int
        :param closable: bool
        :return: PopupMessage
        """

        popup_message_inst = cls(
            text, theme_type=MessageTypes.LOADING, duration=duration, closable=closable, parent=parent)
        popup_message_inst.show()

        return popup_message_inst

    @classmethod
    def config(cls, duration=None, top=None):
        """
        Configures global PopupMesage duration and top setting
        :param duration: int (seconds)
        :param top: int (px)
        """

        if duration is not None:
            cls.DEFAULT_CONFIG['duration'] = duration
        if top is not None:
            cls.DEFAULT_CONFIG['top'] = top

    # =================================================================================================================
    # INTERNAL
    # =================================================================================================================

    def _fade_out(self):
        self._pos_anim.setDirection(QAbstractAnimation.Backward)
        self._pos_anim.start()
        self._opacity_anim.setDirection(QAbstractAnimation.Backward)
        self._opacity_anim.start()

    def _fade_in(self):
        self._pos_anim.start()
        self._opacity_anim.start()

    def _set_proper_position(self, parent):
        parent_parent = parent.parent()
        dcc_window = parent_parent == tp.Dcc.get_main_window()
        parent_geo = parent.geometry()
        pos = parent_geo.topLeft() if dcc_window else parent.mapToGlobal(parent_geo.topLeft())
        # pos = parent_geo.topLeft() if parent.parent() is None else parent.mapToGlobal(parent_geo.topLeft())
        offset = 0
        for child in parent.children():
            if isinstance(child, PopupMessage) and child.isVisible():
                offset = max(offset, child.y())
        base_pos = pos.y() + PopupMessage.DEFAULT_CONFIG.get('top')
        target_x = pos.x() + parent_geo.width() / 2 - 100
        target_y = (offset + 50) if offset else base_pos
        self._pos_anim.setStartValue(QPoint(target_x, target_y - 40))
        self._pos_anim.setEndValue(QPoint(target_x, target_y))

    # =================================================================================================================
    # CALLBACK
    # =================================================================================================================

    def _on_fade_out(self):
        self._fade_out()