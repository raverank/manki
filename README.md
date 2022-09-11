# Manki - A Markdown to Anki Converter

## Installation

- Clone the repository in a directory of your choice and open a terminal in the respective location.
- Install the package with `pip install -e .`

## Usage

### Create a new project

- Navigate into a directory in which you want to create a new project folder
- Execute `manki --new my_project` or `manki -n my_project`
- A new folder will be created which contains several dummy files
  - `manki.toml` contains all project meta data (see )
  - `macros.md` contains some default LaTeX macro definitions for MathJax
  - `questions.md` contains a small selection of example questions.

### Compile

- Navigate into the project directory that contains the `manki.toml` file.
- Execute `manki` (for default Anki-package generation) or `manki -f html` for generation of a html file.

## Manki Configuration

All configurations can be done in the `manki.toml` file that _must exist_ in the project folder.
As the file is read as a TOML file, subsections may be created.
The following options can be set:

| Option                                    | Description                                                                  | Type                   | Example                                     |
| :---------------------------------------- | :--------------------------------------------------------------------------- | :--------------------- | :------------------------------------------ | ---------------------------------------- |
| `general.title`                           | The title of the project                                                     | `str`                  | `"My Title"`                                |
| `general.author`                          | One or multiple authors                                                      | `str                   | List[str]`                                  | `John Doe` or `[John Doe, Foo Bar]`      |
| `general.template`                        | The template that shall be used for the generation                           | `default               | lrt`                                        | `"lrt"`                                  |
| `general.preamble`                        | A premable that is set as description of the pack                            | `str`                  |                                             |
| `input.macros`                            | The file in which macros are defined                                         | `str`                  |                                             |
| `input.sources`                           | The file(s) in which the source files are defined                            | `str                   | List[str]`                                  | `"questions.md"` or `["q1.md", "q2.md"]` |
| `processor.randomquestions.questions`     | List of questions that should be included randomly in to the decks           | `List[List[str, str]]` | `[ [ "Foo?", "Bar!" ], [ "Bla?", "Blu!" ]]` |
| `processor.randomquestions.start_after`   | The minimum number of questions before the first random question is inserted | `int`                  | `2`                                         |
| `processor.randomquestions.max_questions` | Maximum number of random questions                                           | `int`                  | `4`                                         |
