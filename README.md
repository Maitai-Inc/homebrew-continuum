# Homebrew tap for Continuum

`continuum` answers static change-impact questions about the git checkout in the
current directory (Python and TypeScript/JavaScript): what depends on a symbol, how
far a change reaches, and which tests to run. It never runs tests itself.

```bash
brew install maitai-inc/continuum/continuum
```

or, after `brew tap maitai-inc/continuum`, just `brew install continuum`.
The same CLI is on PyPI: `pip install party-continuum`.

```bash
continuum dependents src/app/billing.py::charge
continuum impact
continuum tests --explain
```

`Formula/continuum.rb` is generated and pushed on each release; changes made here
directly are overwritten by the next one.
