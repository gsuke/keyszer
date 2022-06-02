
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import sys
sys.modules["xkeysnail.xorg"] = __import__('lib.xorg_mock',
    None, None, ["get_active_window_wm_class"])
from xkeysnail.output import setup_uinput
from xkeysnail.key import Key, Action
from xkeysnail.config_api import *
from xkeysnail.transform import suspend_keys, \
    resume_keys, \
    boot_config, \
    on_event, \
    suspended
from lib.uinput_stub import UInputStub
from lib.api import *

from evdev.ecodes import EV_KEY, EV_SYN
from evdev.events import InputEvent
import asyncio
import pytest
import pytest_asyncio
import re


_out = None

def setup_function(module):
    global _out
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _out = UInputStub()
    setup_uinput(_out)
    reset_configutation()

async def test_cond_modmap_wins_over_default_modmap():
    modmap({
        Key.RIGHT_CTRL: Key.LEFT_META,
    })
    conditional_modmap(re.compile(r'Emacs'), {
        Key.RIGHT_CTRL: Key.ESC,
    })

    boot_config()

    window("Google Chrome")
    press(Key.RIGHT_CTRL)
    press(Key.F)
    release(Key.F)
    release(Key.RIGHT_CTRL)

    window("Emacs")
    press(Key.RIGHT_CTRL)
    press(Key.F)
    release(Key.F)
    release(Key.RIGHT_CTRL)

    assert _out.keys() == [
        # we're using Chrome, default modmap
        (PRESS, Key.LEFT_META),
        (PRESS, Key.F),
        (RELEASE, Key.F),
        (RELEASE, Key.LEFT_META),
        # remapped RCtrl -> ESC, specific modmap
        (PRESS, Key.ESC),
        (PRESS, Key.F),
        (RELEASE, Key.F),
        (RELEASE, Key.ESC),
    ]   

async def test_when_in_emacs():
    conditional_modmap(re.compile(r'Emacs'), {
        Key.RIGHT_CTRL: Key.ESC,
    })

    boot_config()

    window("Google Chrome")
    press(Key.RIGHT_CTRL)
    press(Key.F)
    release(Key.F)
    release(Key.RIGHT_CTRL)

    window("Emacs")
    press(Key.RIGHT_CTRL)
    press(Key.F)
    release(Key.F)
    release(Key.RIGHT_CTRL)

    assert _out.keys() == [
        # we're using Chrome, unmodified
        (PRESS, Key.RIGHT_CTRL),
        (PRESS, Key.F),
        (RELEASE, Key.F),
        (RELEASE, Key.RIGHT_CTRL),
        # remapped RCtrl -> ESC
        (PRESS, Key.ESC),
        (PRESS, Key.F),
        (RELEASE, Key.F),
        (RELEASE, Key.ESC),
    ]   

@pytest.mark.skip
async def test_sticky_switch_modmaps_midstream():
    pass