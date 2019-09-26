import sublime
import sublime_plugin
from pathlib import Path
import re
from random import random

import subprocess as sp

def get_settings(view, setting, default=None):
    '''Get a setting from the project file if available'''
    try:
        project_data = view.window().project_data()
        project_settings = project_data['settings']['mathademicmarkdown']
    except (KeyError, AttributeError, TypeError):
        project_settings = {}

    if setting in project_settings:
        return project_settings[setting]
    else:
        settings = sublime.load_settings('MathademicMarkdown.sublime-settings')
        return settings.get(setting, default)


def clear_tmpdir():
    tmpdir = Path(sublime.cache_path()) / 'MathademicMarkdown/tmp'
    if not tmpdir.exists():
        tmpdir.mkdir(parents=True)
    elif not tmpdir.is_dir():
        tmpdir.unlink()
        tmpdir.mkdir()
    else:
        files = tmpdir.glob('*.aux')
        for file in files:
            file.unlink()
    return tmpdir


class MathademicMarkdownListener(sublime_plugin.EventListener):
    maths_cache = {}
    phantom_sets_by_buffer = {}
    tmpdir = clear_tmpdir()

    def get_phantom_set(self, view):
        return self.phantom_sets_by_buffer.setdefault(
            view.buffer_id(),
            sublime.PhantomSet(view, 'MathademicMarkdown')
        )

    def on_activated_async(self, view):
        return self.update_maths(view)

    def on_modified_async(self, view):
        return self.update_maths(view)

    def update_maths(self, view):
        maths_regions = view.find_by_selector(
            'text.html.markdown.academicmarkdown '
            'meta.environment.math.block.dollar.latex'
        )

        new_cache = {}
        phantoms = []
        for region in maths_regions:
            math_str = view.substr(region)
            phantom_content = self.maths_cache.get(
                math_str,
                # Changing the numbered_maths setting won't get updated
                # until the cache clears, but just delete and replace a
                # space and it should be fine
                self.create_maths_phantom_content(view, math_str)
            )
            phantom = sublime.Phantom(
                region,
                phantom_content,
                sublime.LAYOUT_BELOW
            )
            phantoms.append(phantom)
            new_cache[math_str] = phantom

        self.get_phantom_set(view).update(phantoms)
        self.maths_cache.clear()
        self.maths_cache.update(new_cache)

    def create_maths_phantom_content(self, view, math_str):
        numbered = get_settings(view, 'numbered_maths', default=False)
        preamble = get_settings(view, 'math_preamble', DEFAULT_MATH_PREAMBLE)
        tex_out = str(random()) + '.tex'
        args = get_settings(view, 'latex_args', ['lualatex', '--interaction=batchmode', '--jobname={}'.format(tex_out)])
        tmpdir = self.tmpdir

        raw_math = math_str.strip('\n$')
        env = choose_math_env(math_str)
        if not numbered:
            env = env + '*'

        latex = ' '.join([
            '\\documentclass[crop=true,multi={},ignorerest=true,png]{{standalone}}'.format(env)
            ] + preamble.split() + [
            '\\begin{document}',
            '\\begin{{{}}}'.format(env),
            ] + raw_math.split() + [
            '\\end{{{}}}'.format(env),
            '\\end{document}'
        ]).encode('utf-8')

        proc = sp.Popen(args, cwd=str(tmpdir), stdin=sp.PIPE)
        proc.communicate(latex)

        html = "<body id=image>Some maths goes here</body>"
        return html


def choose_math_env(math_str):
    if r'\\' in math_str and math_str.count('&') > math_str.count(r'\&'):
        return 'align'
    elif r'\\' in math_str:
        return 'multline'
    else:
        return 'equation'


DEFAULT_MATH_PREAMBLE = '\n'.join([
    "\\usepackage{amsmath}",
    "\\usepackage{amssymb}",
    "\\usepackage{xfrac}",
    "\\usepackage{mathtools}",
    "\\usepackage{physics}",
    "\\usepackage{lualatex-math}",
    "\\usepackage{unicode-math}",
    "\\usepackage{siunitx}"
    "\\newcommand{\\mcvar}[1]{\\ensuremath{\\mathit{#1}}}",
    "\\setmainfont{TeX Gyre Pagella X}",
    "\\setsansfont{DejaVu Sans}",
    "\\setmonofont{PT Mono}",
    "\\setmathfont{TeX Gyre Pagella Math}",
    "\\DeclareInstance{xfrac}{mathdefault}{math}{scale-factor=0.8,scaling=true}",
]).strip()


