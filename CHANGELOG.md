# Arpeggio changelog

All _notable_ changes to this project will be documented in this file.

The format is based on _[Keep a Changelog][keepachangelog]_, and this project
adheres to _[Semantic Versioning][semver]_.

Everything that is documented in the [official docs][ArpeggioDocs] is considered
the part of the public API.

Backward incompatible changes are marked with **(BIC)**. These changes are the
reason for the major version increase so when upgrading between major versions
please take a look at related PRs and issues and see if the change affects you.


## [Unreleased]

- Added support for Python 3.13 and relax restriction on upper Python version.
- Fix parsing of regex rules in peg and cleanpeg syntaxes ([#125]). Thanks
  @smurfix for reporting ([#123]).
- **(BIC)** Removed support for Python 3.6-3.8. The minimal supported version is
  3.9.
- Added sypport for Python 3.12.
- Migrated to pyproject.toml for project configuration.
- Use [ruff] instead of flake8 for linting. ruff can also be used for code
  formating.
- Use [flit] for package building and publishing.
- fix!: non-consuming alternatives in ordered choices **(BIC)** [#96]. Thanks
  @vprat, @mettta and @stanislaw for reporting the issue.

  Now, ordered choice alternatives may succeed even if no input is consumed.
  This means that any infallible expression e.g. `Optional` in an ordered choice
  will always succeed and no further choices will ever be tried.

  Issue [#101] when implemented will detect and report these invalid grammars.

  For the rationale for this change see [this discussion](https://github.com/textX/Arpeggio/commit/db503c961bb7b4da2eddaf1615f66a193a6f9737#r107103641).

- fix!: do not use soft failure in zero/one-or-more **(BIC)**. This is related
  to [#96].

  **Warning:** Previously, we used a kind of "soft failures" of parsing
  expression which were based on treating `None` returned from child expressions
  in repetitions (`ZeroOrMore`, `OneOrMore`) to signalize soft failure and avoid
  infinite loops if the inner expression succeeds without consuming the input.
  While convenient in some cases it has lead to confusion (see #96). Now, the
  parser behaves consistently by always using `NoMatch` to signalize failure.

  This means that now is perfectly possible to make a pathologic grammar that
  will make the parser loop endlessly. For example:

  ```python
  def grammar():
      ZeroOrMore(a), EOF
  def a():
      RegExMatch('.*')
  ```

  Rule `a` is a `RegExMatch` which may succeed by matching empty string thus
  inducing `ZeroOrMore` to repeat endlessly when we reach the end of input.

  In the future Arpeggio might introduce a way to detect these situations during
  parser construction but for now if you find yourself in a situation that the
  parser has stuck watch out for non-consuming matches (especially regex
  matches) inside repetitions or turn on debugging output to see why the parser
  is looping.

  Issue [#101] when implemented will detect and report these invalid grammars.

- fix: #98 suppressed match in zero-or-more [#98]. Thanks @vpavlu for reporting
  the issue.

- fix: empty comments in .peg files hid the next line, commented or not
  ([#124]). Thanks @smurfix for the fix.

[#125]: https://github.com/textX/Arpeggio/issues/125
[#124]: https://github.com/textX/Arpeggio/pull/124
[#123]: https://github.com/textX/Arpeggio/discussions/123
[#101]: https://github.com/textX/Arpeggio/issues/101
[#98]: https://github.com/textX/Arpeggio/issues/98
[#96]: https://github.com/textX/Arpeggio/issues/96
[ruff]: https://github.com/astral-sh/ruff
[flit]: https://flit.pypa.io/
[Unreleased]: https://github.com/textX/Arpeggio/compare/2.0.3...HEAD


## [2.0.3] (released: 2025-09-12)

- fix: memory leak through exception traceback.

[2.0.3]: https://github.com/textX/Arpeggio/compare/2.0.2...2.0.3


## [2.0.2] (released: 2023-07-09)

- fix: drop deprecated `setup_requires` and `tests_require` [#116]. Thanks @kloczek.

[#116]: https://github.com/textX/Arpeggio/issues/116
[2.0.2]: https://github.com/textX/Arpeggio/compare/2.0.1...2.0.2


## [2.0.1] (released: 2023-07-09)

- fix: replace `\n` with `\\n` in error reports for matches [#99]. Thanks
  @mettta and @stanislaw.

[#99]: https://github.com/textX/Arpeggio/pull/99
[2.0.1]: https://github.com/textX/Arpeggio/compare/2.0.0...2.0.1


## [2.0.0] (released: 2022-03-20)

- Added `eval_attrs` call to `NoMatch` exceptions ([ebfd60]). See [the
  docs](https://textx.github.io/Arpeggio/latest/handling_errors/).
- Dropped support for deprecated Python versions. The lowest supported version
  is 3.6. **(BIC)**


[ebfd60]: https://github.com/textX/Arpeggio/commit/ebfd60a7330cd5e6aaacfd5be7001be0f7506ce8
[2.0.0]: https://github.com/textX/Arpeggio/compare/1.10.2...2.0.0


## [1.10.2] (released: 2021-04-25)

- Added EditorConfig configuration ([#77]). Thanks KOLANICH@GitHub
- Fixed parsing of version from `setup.py` when global encoding isn't UTF-8
  ([#86]). Thanks neirbowj@GitHub
- Fix repetition termination on a successful empty separator match ([#92]).

[1.10.2]: https://github.com/textX/Arpeggio/compare/1.10.1...1.10.2
[#92]: https://github.com/textX/Arpeggio/issues/92
[#86]: https://github.com/textX/Arpeggio/pull/86
[#77]: https://github.com/textX/Arpeggio/pull/77


## [1.10.1] (released: 2020-11-01)

- Fix packaging, exclude examples from wheel. Thanks mgorny@GitHub ([#83])

[1.10.1]: https://github.com/textX/Arpeggio/compare/v1.10.0...1.10.1
[#83]: https://github.com/textX/Arpeggio/pull/83


## [1.10.0] (released: 2020-11-01)

- Fix reporting duplicate rule names in `NoMatch` exception ([a1f14bede])
- Raise `AttributeError` when accessing unexisting rule name on parse tree node.
  ([#82])
- Added `tree_str` method to parse tree nodes for nice string representation of
  parse trees. ([#76])
- Added parse tree node suppression support and overriding of special Python
  rule syntax. (#76)
- UnorderedGroup matching made deterministic ([#73])


[a1f14bede]: https://github.com/textX/Arpeggio/commit/a1f14bedec14aa742c5a40c15be240d3a31addfa
[#82]: https://github.com/textX/Arpeggio/issues/82
[#76]: https://github.com/textX/Arpeggio/issues/76
[#73]: https://github.com/textX/Arpeggio/issues/73
[1.10.0]: https://github.com/textX/Arpeggio/compare/v1.9.2...1.10.0


## [v1.9.2] (released: 2019-10-05)

  - Added explicit Python versions in setup.py classifiers ([#65])
  - Removed pytest version constraint and fixed tests to work with both 5.x and
    older versions. ([#57])

[#65]: https://github.com/textX/Arpeggio/issues/65
[#57]: https://github.com/textX/Arpeggio/issues/57
[v1.9.2]: https://github.com/textX/Arpeggio/compare/v1.9.1...v1.9.2


## [v1.9.1] (released: 2019-09-28)

  - Lowered the required pytest version for running tests as we'll still support
    Python 2.7 until its EOL.
  - Fixed problem with `OrderedChoice` which hasn't maintained `skipws/ws`
    state. [#61]
    Reported at https://github.com/textX/textX/issues/205
  - Various fixes in the docs, docstrings and examples. Thanks mcepl@GitHub and
    zetaraku@GitHub.
  - docs support for different versions thanks to
    [mike](https://github.com/jimporter/mike)


[#61]: https://github.com/textX/Arpeggio/issues/61
[v1.9.1]: https://github.com/textX/Arpeggio/compare/v1.9.0...v1.9.1


## [v1.9.0] (released: 2018-07-19)

  - Added `extra_info` param to `Terminal` for additional information.
    Used by textX.
  - Fixed problem with version string reading in non-UTF-8 environments.
    Thanks sebix@GitHub.

[v1.9.0]: https://github.com/textX/Arpeggio/compare/v1.8.0...v1.9.0


## [v1.8.0] (released: 2018-05-16)

  - Fixed issue [#43].
    *Backward incompatible change* for cleanpeg comment syntax.
  - Added `file` parser param used for `DebugPrinter` to allow the
    output stream to be changed from stdout. This allows doctests to
    continue to work. Thanks ianmmoir@GitHub.

[#43]: https://github.com/textX/Arpeggio/issues/43
[v1.8.0]: https://github.com/textX/Arpeggio/compare/v1.7.1...v1.8.0


## [v1.7.1] (released: 2018-02-10)

  - Fixed bug in comment parsing optimization.

[v1.7.1]: https://github.com/textX/Arpeggio/compare/v1.7...v1.7.1


## [v1.7] (released: 2017-11-17)

  - Added `re_flag` parameter to `RegExMatch` constructor. Thanks
    Aluriak@GitHub.
  - Fix in grammar language docs. Thanks schmittlauch@GitHub.
  - Small fixes in examples.

[v1.7]: https://github.com/textX/Arpeggio/compare/v1.6.1...v1.7

## [v1.6.1] (released: 2017-05-15)

  - Fixed bug in unordered group with optional subexpressions.

[v1.6.1]: https://github.com/textX/Arpeggio/compare/v1.6...v1.6.1

## [v1.6] (released: 2017-05-15)

  - Dropped support for Python 3.2.
  - Improved error reporting (especially for `Not` Parsing Expression).
  - `line,col` attributes are now available on `NoMatch` exception.
  - Fixed issue [#31] - a subtle bug in empty nested parses.
  - Issue [#32] - improvements and fixes in escape sequences support.
    Thanks smbolton@github!
  - Added `position_end` attribute on parse tree nodes with the position
    in the input stream where the given match ends.
  - Added support for unordered groups (`UnorderedGroup` class). See the docs.
  - Support for separator expression in repetitions (`sep` parameter).
    See the docs.
  - Various code/docs cleanup.

[#31]: https://github.com/textX/Arpeggio/issues/31
[#32]: https://github.com/textX/Arpeggio/issues/32
[v1.6]: https://github.com/textX/Arpeggio/compare/v1.5...v1.6

## [v1.5] (released: 2016-05-31)

  - Significant performance improvements (see textX issue [#22])
  - Added new performance tests to keep track of both speed and memory
    consumption.
  - Memoization is disabled by default. Added `memoization` parameter to
    the `Parser` instantiation.

[#22]: https://github.com/textX/textX/issues/22
[v1.5]: https://github.com/textX/Arpeggio/compare/v1.4...v1.5

## [v1.4] (released: 2016-05-05)

  - Support for parse tree node suppression. Used for textX `-` operator.
  - Render `-` for suppressed ParsingExpression on dot graphs.

[v1.4]: https://github.com/textX/Arpeggio/compare/v1.3.1...v1.4

## [v1.3.1] (released: 2016-04-28)

  - Some smaller changes/fixes in internal API.
  - Smaller updates to docs.

[v1.3.1]: https://github.com/textX/Arpeggio/compare/v1.3...v1.3.1

## [v1.3] (released: 2016-03-03)

  - Improved error reporting (issue [#25]). On the point of error all possible
    matches will be reported now.
  - Fixed bug with regex that succeeds with empty string in repetitions
    (issue [#26]).
  - Various fixes in examples and the docs.
  - Significant performance improvement for parsing of large files. This fix
    also changes handling of `^` in regex matches. Now `^` will match on the
    beginning of the input and beginning of new line.
  - Performance improvements in comment parsing.

[#25]: https://github.com/textX/Arpeggio/issues/25
[#26]: https://github.com/textX/Arpeggio/issues/26
[v1.3]: https://github.com/textX/Arpeggio/compare/v1.2.1...v1.3

## [v1.2.1] (released: 2015-11-10)

  - Fixing error reporting that wasn't taking into account successful matches in
    optionals.
  - Slightly improved debug prints.

[v1.2.1]: https://github.com/textX/Arpeggio/compare/v1.2...v1.2.1

## [v1.2] (released: 2015-10-31)

  - Docs has been migrated to [MkDocs] and restructured. A lot of new additions
    have been made and three full length tutorials.
  - Examples refactoring and restructuring.
  - Fixing whitespace handling for str matches loaded from external PEG file.
  - Added travis configuration to test for 2.7, 3.2-3.5 Python versions.

[v1.2]: https://github.com/textX/Arpeggio/compare/v1.1...v1.2

## [v1.1] (released: 2015-08-27)

  - Reworking `NoMatch` exception handling code.
  - Some optimization tweaks. Removed unnecessary exception handling.
  - Improved debug printings.
  - Fix in ordered choice with optional matches (issue [#20])
  - Fixing parser invalid state after handling non-string inputs
    (thanks Santi Villalba - sdvillal@github)
  - Some fixes in conversion to utf-8 encoding.
  - Various improvements and additions to the tests.

[#20]: https://github.com/textX/Arpeggio/issues/20
[v1.1]: https://github.com/textX/Arpeggio/compare/v1.0...v1.1

## [v1.0] (released: 2015-04-14)

  - Functionally identical to v0.10. It is just the time to go
    production-stable ;)

[v1.0]: https://github.com/textX/Arpeggio/compare/v0.10...v1.0

## [v0.10] (released: 2015-02-10)

  - Documentation - http://arpeggio.readthedocs.org/en/latest/
  - `autokwd` parser parameter. Match on word boundaries for keyword-like
    string matches.
  - `skipws` and `ws` parameters for `Sequence`.
  - Improvements in error reporting.

[v0.10]: https://github.com/textX/Arpeggio/compare/v0.9...v0.10

## [v0.9] (released: 2014-10-16)

  - Visitor pattern support for semantic analysis - issue 15
  - Alternative PEG syntax (`arpeggio.cleanpeg` module) - issue 11
  - Support for unicode in grammars.
  - Python 2/3 compatibility for unicodes.

[v0.9]: https://github.com/textX/Arpeggio/compare/v0.8...v0.9

## [v0.8] (released: 2014-09-20)

  - Support for eolterm modifier in repetitions.
  - Support for custom regex match string representation.
  - Various bugfixes.
  - Improved debug messages.

[v0.8]: https://github.com/textX/Arpeggio/compare/v0.7...v0.8

## [v0.7] (released: 2014-08-16)

  - Parse tree navigation
  - Better semantic action debugging output.
  - Tests reorganization and cleanup.
  - Examples cleanup.
  - Reference resolving unification in parser constructions.
  - Default semantic actions and automatic terminal suppressing during semantic
    analysis.
  - PEG language support refactoring and code cleaning.

[v0.7]: https://github.com/textX/Arpeggio/compare/v0.6...v0.7

## [v0.6] (released: 2014-06-06)

  - Support for Python 3 (issue [#7])
  - Matched rules available as attributes of non-terminals (issue [#2])
  - Lexical rules support (issue [#6]). Implemented as `Combine` decorator.

[#7]: https://github.com/textX/Arpeggio/issues/7
[#6]: https://github.com/textX/Arpeggio/issues/6
[#2]: https://github.com/textX/Arpeggio/issues/2
[v0.6]: https://github.com/textX/Arpeggio/compare/v0.5...v0.6

## [v0.5] (released: 2014-02-02)

  - Bugfixes
  - Examples
  - Parse tree reduction for one-child non-terminals.

[v0.5]: https://github.com/textX/Arpeggio/compare/v0.1-dev...v0.5

## v0.1-dev (released: 2009-09-15) - Initial release

  - Basic error reporting.
  - Basic support for comments handling (needs refactoring)
  - Raw parse tree.
  - Support for semantic actions with ability to transform parse
      tree to semantic representation - aka Abstract Semantic Graphs (see examples).

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/spec/v2.0.0.html
[MkDocs]: https://www.mkdocs.org/
[ArpeggioDocs]: http://textx.github.io/Arpeggio/latest/
