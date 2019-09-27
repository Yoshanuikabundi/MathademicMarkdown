from functools import partial

import sublime
import sublime_plugin

from LaTeXTools.st_preview.preview_math import (
    MathPreviewPhantomListener,
    default_latex_template
)

from LaTeXTools.latextools_utils.settings import _get_setting
from LaTeXTools.latextools_utils.utils import run_on_main_thread


# Have view settings prefixed with 'mathademicmarkdown_' override everything
def get_setting(setting, default=None, view=None):
    if default is not None:
        return run_on_main_thread(
            partial(_mm_get_setting, setting, default, view),
            default_value=default)
    else:
        return run_on_main_thread(
            partial(_mm_get_setting, setting, view=view))


def _mm_get_setting(setting, default=None, view=None):
    try:
        if view is None:
            view_settings = sublime.active_window().active_view().settings()
        elif isinstance(view, sublime.View):
            view_settings = view.settings()
        else:
            view_settings = {}
    except Exception:
        # no view defined or view invalid
        view_settings = {}

    result = view_settings.get('mathademicmarkdown_' + setting)

    if result is not None:
        return result
    else:
        return _get_setting(setting, default=None, view=None)


class MarkdownMathPreviewPhantomListener(MathPreviewPhantomListener):
    # Hack to stop _create_document from stopping the main thread
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.guess_env = get_setting(
            "guess_math_environment",
            False
        )

    # Make applicable on MathademicMarkdown files
    @classmethod
    def is_applicable(cls, settings):
        return (
            settings.get('syntax')
            == 'Packages/MathademicMarkdown/MathademicMarkdown.sublime-syntax'
        )

    # Redefine hooks so that sublime sees them
    def on_selection_modified(self, *args, **kwargs):
        # Well, this one also updates the guess_math_environment setting
        self.guess_env = get_setting(
            "guess_math_environment",
            False
        )
        super().on_selection_modified(*args, **kwargs)

    def on_after_modified_async(self, *args, **kwargs):
        super().on_after_modified_async(*args, **kwargs)

    def on_modified(self, *args, **kwargs):
        super().on_modified(*args, **kwargs)

    def on_after_selection_modified_async(self, *args, **kwargs):
        super().on_after_selection_modified_async(*args, **kwargs)

    def on_navigate(self, *args, **kwargs):
        super().on_navigate(*args, **kwargs)

    # Rewrite the actual _create_document method
    def _create_document(self, scope, color):
        view = self.view
        content = view.substr(scope)
        env = None

        if content[0:2] == "$$" and self.guess_env:
            if r'\\' in content and content.count('&') > content.count(r'\&'):
                env = 'align'
            elif r'\\' in content:
                env = 'multline'
            else:
                env = 'equation'
            content = content.strip('$\n')
            starred_env = True
            offset = 0
        # calculate the leading and remaining characters to strip off
        # if not present it is surrounded by an environment
        elif content[0:2] in ["\\[", "\\(", "$$"]:
            offset = 2
        elif content[0] == "$":
            offset = 1
        else:
            offset = 0
            # if there is no offset it must be surrounded by an environment
            # get the name of the environment
            scope_end = scope.end()
            line_reg = view.line(scope_end)
            after_reg = sublime.Region(scope_end, line_reg.end())
            after_str = view.substr(after_reg)
            m = re.match(r"\\end\{([^\}]+?)(\*?)\}", after_str)
            if m:
                env = m.group(1)
                starred_env = bool(m.group(2))

        # create the opening and closing string
        if offset:
            open_str = content[:offset]
            close_str = content[-offset:]
            # strip those strings from the content
            content = content[offset:-offset]
        elif env:
            star = "*" if env not in self.no_star_env or starred_env else ""
            # add a * to the env to avoid numbers in the resulting image
            open_str = "\\begin{{{env}{star}}}".format(**locals())
            close_str = "\\end{{{env}{star}}}".format(**locals())
        else:
            open_str = "\\("
            close_str = "\\)"

        # strip the content
        content = content.strip()

        document_content = (
            "{open_str}\n{content}\n{close_str}"
            .format(**locals())
        )

        try:
            latex_template = self.template_contents[self.latex_template_file]
            if not latex_template:
                raise Exception("Template must not be empty!")
        except Exception:
            latex_template = default_latex_template

        if color.startswith("#"):
            color = color[1:].upper()
            set_color = "\\color[HTML]{{{color}}}".format(color=color)
        else:
            set_color = "\\color{{{color}}}".format(color=color)

        latex_document = (
            latex_template
            .replace("<<content>>", document_content, 1)
            .replace("<<set_color>>", set_color, 1)
            .replace("<<packages>>", self.packages_str, 1)
            .replace("<<preamble>>", self.preamble_str, 1)
        )

        return latex_document
