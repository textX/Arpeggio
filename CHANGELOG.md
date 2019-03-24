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

[Unreleased]: https://github.com/textX/Arpeggio/compare/v1.9.0...HEAD

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
  - Support for semantic actions with abbility to transform parse 
      tree to semantic representation - aka Abstract Semantic Graphs (see examples).

[keepachangelog]: https://keepachangelog.com/
[semver]: https://semver.org/spec/v2.0.0.html
[MkDocs]: https://www.mkdocs.org/
[ArpeggioDocs]: http://textx.github.io/Arpeggio/latest/
