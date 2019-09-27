from __future__ import print_function


def is_bib_buffer(view, point=0):
    return (
        view.score_selector(point, 'text.bibtex') > 0 or
        is_biblatex_buffer(view, point)
    )


def is_biblatex_buffer(view, point=0):
    return view.score_selector(point, 'text.biblatex') > 0

try:
    from mm_utils.settings import get_setting
except ImportError:
    from .settings import get_setting

def using_miktex():
    platform_settings = get_setting(sublime.platform(), {})
    distro = platform_settings.get('distro', '')

    if sublime.platform() == 'windows':
        return distro in ['miktex', '']
    else:
        return distro == 'miktex'
