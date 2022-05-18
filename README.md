# Manki - A Markdown to Anki Converter

## Template Variables

All templates can contain placeholders (using two braces: `{{placeholder}}`) that get filled with the respective value when the output is generated.
Different exporters may provide different variables.
As all variables are controlled via the structure given in the `manki.toml`-File, those variables may be used as well.
For example, the value of the author given in the `manki.toml` can be used in the template via `{{general.author}}`

### General Variables

Those variables can be used in all templates.

| Variable         | Effect                                                   |
| :--------------- | :------------------------------------------------------- |
| general.author   | Prints the authors given in the toml file.               |
| general.preamble | Outputs the preamble given in the toml file.             |
| general.title    | Outputs the title given in the toml file.                |
| general.template | Outputs the name of the template given in the toml file. |
| 
