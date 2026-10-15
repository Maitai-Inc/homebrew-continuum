"""Exercise release branch staging against a real disposable Git remote."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / '.github/scripts/propose_formula.sh'

class ProposeFormulaTest(unittest.TestCase):
    def test_candidate_is_idempotent_and_never_updates_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote, work = root / 'remote.git', root / 'work'
            def run(*args, cwd=None, env=None):
                return subprocess.check_output(args, cwd=cwd, env=env, text=True).strip()
            run('git', 'init', '--bare', str(remote))
            run('git', 'init', '-b', 'main', str(work))
            run('git', 'config', 'user.name', 'Fixture', cwd=work)
            run('git', 'config', 'user.email', 'fixture@example.invalid', cwd=work)
            (work / 'Formula').mkdir()
            formula = work / 'Formula/continuum.rb'
            formula.write_text('old release\n')
            run('git', 'add', '.', cwd=work)
            run('git', 'commit', '-m', 'initial', cwd=work)
            run('git', 'remote', 'add', 'origin', str(remote), cwd=work)
            run('git', 'push', 'origin', 'main', cwd=work)
            main = run('git', 'rev-parse', 'main', cwd=work)
            summary = root / 'summary.md'
            env = dict(os.environ, VERSION='1.2.3', GITHUB_REPOSITORY='example/tap', GITHUB_STEP_SUMMARY=str(summary))
            formula.write_text('tested release\n')
            run('bash', str(SCRIPT), cwd=work, env=env)
            first = run('git', 'ls-remote', '--heads', 'origin', cwd=work)
            self.assertEqual(run('git', '--git-dir', str(remote), 'rev-parse', 'main'), main)
            candidates = [line.split()[1] for line in first.splitlines() if '/codex/' in line]
            self.assertEqual(len(candidates), 1)
            branch = candidates[0]
            self.assertEqual(run('git', '--git-dir', str(remote), 'show', branch + ':Formula/continuum.rb'), 'tested release')
            run('bash', str(SCRIPT), cwd=work, env=env)
            self.assertEqual(run('git', 'ls-remote', '--heads', 'origin', cwd=work), first)
            self.assertIn('https://github.com/example/tap/compare/main...codex/', summary.read_text())
            self.assertIn('expand=1', summary.read_text())

if __name__ == '__main__':
    unittest.main()
