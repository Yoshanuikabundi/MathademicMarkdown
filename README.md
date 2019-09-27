# MathademicMarkdown
This extension to AcademicMarkdown adds an MathademicMarkdown language variant that supports more of Pandoc's syntax features.

## Acknowledgements

This package would not exist without the efforts of the authors of the MarkdownEditing, AcademicMarkdown and LaTeXTools packages, all of which I have borrowed from extensively.

## Requirements
For intended functionality, MathademicMarkdown requires
 - [MarkdownEditing](https://packagecontrol.io/packages/MarkdownEditing) for a few settings
 - [LaTeXTools](https://packagecontrol.io/packages/AcademicMarkdown) for maths previews

## Features
- Highlighting for [CriticMarkup](http://criticmarkup.com/) notation
- Highlighting for Pandoc's `@Citekey` notation
- Highlighting for inline LaTeX, including maths
- Highlighting for `^[]` footnote notation
- Highlighting for Pandoc's raw attribute extension, both in blocks and inline
- Support for the [LaTeXTools](https://packagecontrol.io/packages/LaTeXTools) math preview feature

## Installation
MathademicMarkdown can be installed from a source archive by unzipping into your Sublime Text "Packages" folder (make sure the extracted folder is named MathademicMarkdown).

## Citations

[JAMCiter](https://github.com/yoshanuikabundi/JAMCiter) - SublimeText 3 plugin to insert citations from a Bibtex file, or the CrossRef and PubMed web APIs into your markdown file
