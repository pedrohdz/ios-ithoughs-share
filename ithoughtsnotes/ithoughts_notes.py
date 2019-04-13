#!/usr/bin/env python
# pylint: disable=missing-docstring

from urllib import parse
import webbrowser
import logging as log
import os

import requests
from bs4 import BeautifulSoup

from ithoughtsnotes.mind_maps import MindMaps


DEFAULT_CONFIG_DIR = os.path.abspath(
    os.path.expanduser('~/Documents/.ios-ithoughs-share'))


class StateHandler():
    def __init__(self):
        self._log = log.getLogger(type(self).__name__)

    @property
    def log(self):
        return self._log

    def handle(self, state_data, callback):
        # pylint: disable=unused-argument
        self.log.info('Handeling')


class UiPanelStateHandler(StateHandler):
    def __init__(self, view):
        super().__init__()
        self._view = view

    @property
    def view(self):
        return self._view

    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        self.view['cancel'].action = self.cancel_callback(state_data, callback)
        self.view['ok'].action = self.ok_callback(state_data, callback)

    def handle_ok(self, sender, state_data):
        pass

    def handle_cancel(self, sender, state_data):
        pass

    def ok_callback(self, state_data, callback):
        # pylint: disable=invalid-name
        def function(sender):
            # pylint: disable=unused-argument
            self.log.info('OK')
            self.handle_ok(sender, state_data)
            self._view.close()
            self._view.wait_modal()
            callback('FORWARD')
        return function

    def cancel_callback(self, state_data, callback):
        def function(sender):
            # pylint: disable=unused-argument
            self.log.info('Canceling')
            self.handle_cancel(sender, state_data)
            self._view.close()
            self._view.wait_modal()
            callback('CANCEL')
        return function


# pylint: disable=too-few-public-methods,multiple-statements
class Finisher(StateHandler): pass  # NOQA
class Canceler(StateHandler): pass  # NOQA
# pylint: enable=too-few-public-methods,multiple-statements


class StateData():
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.initializer = None
        self.url_editor = None
        self.note_editor = None
        self.map_picker = None
        self.ithoughts_dispatcher = None


class Initializer(StateHandler):
    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        self.create_dir_if_missing(DEFAULT_CONFIG_DIR)
        state_data.initializer = {
            'mind_maps_file': os.path.join(DEFAULT_CONFIG_DIR,
                                           'mind_maps.json'),
            'input_url': get_input_url()}
        callback('FORWARD')

    def create_dir_if_missing(self, directory):
        try:
            os.makedirs(directory)
            self.log.info('Created configuration directory: %s', directory)
        except FileExistsError:
            self.log.info(
                'Configuration directory already exists: %s', directory)


class UrlEditor(UiPanelStateHandler):
    def __init__(self, view=None):
        if not view:
            # pylint: disable=import-error,no-member
            import ui
            view = ui.load_view('url_editor')
        super().__init__(view)

    # pylint: disable=too-few-public-methods
    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        state_data.url_editor = None
        self.view['url'].text = state_data.initializer['input_url']
        self.view.present('sheet')

    def handle_ok(self, sender, state_data):
        state_data.url_editor = {
            'url': self.view['url'].text}


class NoteEditor(UiPanelStateHandler):
    def __init__(self, view=None):
        if not view:
            # pylint: disable=import-error,no-member
            import ui
            view = ui.load_view('ithoughts_notes')
        super().__init__(view)

    # pylint: disable=too-few-public-methods
    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        state_data.note_editor = None
        web_note = WebPageNote.from_url(state_data.url_editor['url'])
        self.view['title'].text = web_note.title
        self.view['url'].text = web_note.url
        self.view['body'].text = web_note.body
        self.view.present('sheet')

    def handle_ok(self, sender, state_data):
        state_data.note_editor = {
            'title': self.view['title'].text,
            'url': self.view['url'].text,
            'body': self.view['body'].text}


class MapPicker(UiPanelStateHandler):
    def __init__(self, view=None, list_data_source=None, mind_maps=None,
                 form_dialog=None):
        # pylint: disable=import-error,no-member
        if not view:
            import ui
            view = ui.load_view('map_picker')
        if not list_data_source:
            import ui
            list_data_source = ui.ListDataSource(list())
        if not form_dialog:
            import dialogs
            form_dialog = dialogs.form_dialog
        try:
            import ui
            capitalization = ui.AUTOCAPITALIZE_WORDS
        except ModuleNotFoundError:
            capitalization = None
        super().__init__(view)
        self.list_data_source = list_data_source
        self.mind_maps = mind_maps
        self.form_dialog = form_dialog
        self.capitalization = capitalization

    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        # Setup actions
        self.list_data_source.action = self.select
        self.list_data_source.delete_enabled = False
        self.view['map_list_table_view'].data_source = self.list_data_source
        self.view['map_list_table_view'].delegate = self.list_data_source
        self.view['ok'].enabled = False
        self.view['add'].action = self.add_callback(state_data, callback)

        # Populate list
        if not self.mind_maps:
            mind_maps_file = state_data.initializer['mind_maps_file']
            self.mind_maps = MindMaps.loadf(mind_maps_file, create=True)
        self.list_data_source.items = self.mind_maps
        self.view.present('sheet')

    def handle_ok(self, sender, state_data):
        index = self.list_data_source.selected_row
        map_path = self.list_data_source.items[index]
        self.log.info('Item selected: %s', map_path)
        state_data.map_picker = {'map_path': map_path}

    def add_callback(self, _, callback):
        # pylint: disable=invalid-name
        def function(sender):
            # pylint: disable=unused-argument
            self.log.info('Go to add mind map')
            self._view.close()
            self._view.wait_modal()
            callback('ADD_MIND_MAP')
        return function

    def select(self, sender):
        self.log.info('Picked = %s', sender.selected_row)
        if sender.selected_row > -1:
            self.view['ok'].enabled = True
        else:
            self.view['ok'].enabled = False


class MapAdder(UiPanelStateHandler):
    def __init__(self, view=None):
        # pylint: disable=import-error,no-member
        if not view:
            import ui
            view = ui.load_view('map_adder')
        try:
            import ui
            capitalization = ui.AUTOCAPITALIZE_WORDS
        except ModuleNotFoundError:
            capitalization = None
        super().__init__(view)
        self.capitalization = capitalization

    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        self.view['new_path'].text = '/Notes/New Map Name'
        self.view.present('sheet')

    def handle_ok(self, sender, state_data):
        map_path = self.view['new_path'].text
        self.log.info('Creating mind map: %s', map_path)
        self.add_to_mind_maps(state_data.initializer['mind_maps_file'],
                              map_path)

        url = 'https://github.com/pedrohdz/ios-ithoughs-share'
        body = ('## Mind Map Inbox\n\n'
                'WARNING - Do not modify this note\n\n'
                'New notes are attached to this one so they are easier to '
                'find and process.\n\n'
                '_Inbox for notes created by [ios-ithoughs-share]({})_.'
                .format(url))
        title = '# Mind Map Inbox'
        ithoughs_url = build_ithoughts_url(map_path, title, url, body,
                                           create=True)
        dispatch(ithoughs_url)

    def add_to_mind_maps(self, mind_maps_file, map_path):
        self.log.info('Adding "%s" to "%s"', map_path, mind_maps_file)
        mind_maps = MindMaps.loadf(mind_maps_file, create=True)
        mind_maps.add(map_path)
        mind_maps.dumpf()


class IThoughtsDispatcher(StateHandler):
    def handle(self, state_data, callback):
        super().handle(state_data, callback)
        map_path = state_data.map_picker['map_path']
        ithoughs_url = build_ithoughts_url(
            map_path,
            state_data.note_editor['title'],
            state_data.note_editor['url'],
            state_data.note_editor['body'],
            create=False)
        dispatch(ithoughs_url)
        callback('FORWARD')


class _StateMetaClass(type):
    @property
    def start(cls):
        return 'START'

    @property
    def initialize(cls):
        return 'INITIALIZE'

    @property
    def edit_url(cls):
        return 'URL_EDITOR'

    @property
    def edit_note(cls):
        return 'NOTE_EDITOR'

    @property
    def pick_mind_map(cls):
        return 'MAP_PICKER'

    @property
    def add_mind_map(cls):
        return 'MAP_ADDER'

    @property
    def create_ithoughs_note(cls):
        return 'ITHOUGH_DISPATCHER'

    @property
    def end(cls):
        return 'END'

    @property
    def cancel(cls):
        return 'CANCEL'


class State(metaclass=_StateMetaClass):
    # pylint: disable=too-few-public-methods
    pass


class StateDispatcher():
    state_map = {
        State.start: {
            'FORWARD': State.initialize},
        State.initialize: {
            'FORWARD': State.pick_mind_map},
        State.pick_mind_map: {
            'FORWARD': State.edit_url,
            'ADD_MIND_MAP': State.add_mind_map},
        State.add_mind_map: {
            'FORWARD': State.end},
        State.edit_url: {
            'FORWARD': State.edit_note},
        State.edit_note: {
            'FORWARD': State.create_ithoughs_note},
        State.create_ithoughs_note: {
            'FORWARD': State.end},
        State.cancel: {
            'FORWARD': State.end},
    }

    def __init__(self,
                 state_data=None,
                 initializer=None,
                 url_editor=None,
                 note_editor=None,
                 map_picker=None,
                 map_adder=None,
                 ithoughts_dispatcher=None,
                 finisher=None,
                 canceler=None):
        # pylint: disable=too-many-arguments
        self._log = log.getLogger(type(self).__name__)

        if not state_data:
            state_data = StateData()

        if not initializer:
            initializer = Initializer()

        if not url_editor:
            url_editor = UrlEditor()

        if not note_editor:
            note_editor = NoteEditor()

        if not map_picker:
            map_picker = MapPicker()

        if not map_adder:
            map_adder = MapAdder()

        if not ithoughts_dispatcher:
            ithoughts_dispatcher = IThoughtsDispatcher()

        if not finisher:
            finisher = Finisher()

        if not canceler:
            canceler = Canceler()

        self._handlers = {
            State.edit_url: url_editor,
            State.initialize: initializer,
            State.edit_note: note_editor,
            State.pick_mind_map: map_picker,
            State.add_mind_map: map_adder,
            State.create_ithoughs_note: ithoughts_dispatcher,
            State.end: finisher,
            State.cancel: canceler}
        self._state_data = state_data
        self._current_state = State.start
        self._canceled = False

    @property
    def log(self):
        return self._log

    @property
    def current_state(self):
        return self._current_state

    @property
    def is_end(self):
        return self.current_state == State.end

    @property
    def is_canceled(self):
        return self._canceled

    def next_state(self, step):
        last_state = self.current_state
        if step != 'CANCEL':
            new_state = StateDispatcher.state_map[last_state][step]
        else:
            new_state = State.cancel
            self._canceled = True
        self.log.info('Changing from "%s" to "%s"', last_state, new_state)
        self._current_state = new_state
        self._handlers[new_state].handle(self._state_data, self.next_state)


def get_input_url():
    # pylint: disable=import-error
    import appex
    url = appex.get_url()
    return (url if url else
            'http://omz-software.com/pythonista/docs/ios/dialogs.html')


def build_ithoughts_url(mind_map_path, title, url, body, create):
    base_url = 'ithoughts://x-callback-url'
    resource = 'makeMap' if create else 'amendMap'
    arguments = {
        'format': 'md',
        'link': url,
        'note': body,
        'path': mind_map_path,
        'style': 'Chalkboard',
        'text': title,
    }
    if not create:
        arguments['target'] = r'Mind\s+Map\s+Inbox'
    return '{}/{}?{}'.format(
        base_url,
        resource,
        parse.urlencode(arguments, quote_via=parse.quote))


def dispatch(url):
    try:
        # pylint: disable=bare-except
        webbrowser.open(url)
    except:  # NOQA
        # pylint: disable=import-error
        from objc_util import UIApplication, nsurl
        app = UIApplication.sharedApplication()
        app.openURL_(nsurl(url))


class WebPageNote():
    def __init__(self, url, html):
        self._url = url
        self._soup = BeautifulSoup(html, 'html.parser')

    @classmethod
    def from_url(cls, url):
        return cls(url, requests.get(url).text)

    @property
    def url(self):
        return self._url

    @property
    def raw_title(self):
        return self._soup.title.text.strip(' \t\n\r')

    @property
    def title(self):
        return '# {}'.format(self.raw_title)

    @property
    def body(self):
        description = ''
        blocks_processed = 0
        for block in self._soup.find_all('p'):
            text = block.text.strip(' \t\n\r')
            if not text:
                continue
            description += (
                ('\n\n' if description else '')
                + text)
            blocks_processed += 1
            if blocks_processed > 4:
                break
        return ('## {}\n\n{}\n\n_[quick link]({})_'
                .format(self.raw_title, description, self.url))


def main():
    dispatcher = StateDispatcher()
    dispatcher.next_state('FORWARD')


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    main()
