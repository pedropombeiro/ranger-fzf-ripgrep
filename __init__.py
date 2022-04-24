from ranger.api.commands import Command

class fzf_rg_select(Command):
    """
    :fzf_rg_select
    Find a file by contents using ripgrep and fzf.
    With a prefix argument to select only directories.

    See: https://github.com/BurntSushi/ripgrep, https://github.com/junegunn/fzf
    """

    def execute(self):
        import subprocess
        import os
        from ranger.ext.get_executables import get_executables

        if self.arg(1):
            search_string = self.rest(1)
        else:
            self.fm.notify("Usage: fzf_rg_select <search string>", bad=True)
            return

        if 'fzf' not in get_executables():
            self.fm.notify('Could not find fzf in the PATH.', bad=True)
            return

        rg = None
        if 'rg' in get_executables():
            rg = 'rg'
        else:
            self.fm.notify('Could not find rg in the PATH.', bad=True)
            return

        hidden = ('--hidden' if self.fm.settings.show_hidden else '')
        fzf_default_command = '{} \'{}\' --column --line-number --no-heading --color=always --smart-case {}'.format(
            rg, search_string, hidden
        )

        env = os.environ.copy()
        env['FZF_DEFAULT_COMMAND'] = fzf_default_command
        env['FZF_DEFAULT_OPTS'] = '--delimiter : --height=40% --layout=reverse --ansi --preview="{}"'.format('''
            (
                bat --style=full --color=always --highlight-line {2} {1} ||
                cat {}
            ) 2>/dev/null | head -n 100
        ''')

        fzf = self.fm.execute_command('fzf --no-multi', env=env,
                                      universal_newlines=True, stdout=subprocess.PIPE)
        stdout, _ = fzf.communicate()
        if fzf.returncode == 0:
            selected = os.path.abspath(stdout.strip().split(':', 1)[0])
            if os.path.isdir(selected):
                self.fm.cd(selected)
            else:
                self.fm.select_file(selected)
