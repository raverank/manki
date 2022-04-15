from html.parser import HTMLParser
import markdown
from bs4 import BeautifulSoup

extensions = ["pymdownx.arithmatex", "md_in_html"]

MATHJAX_SRC = """<script type="text/javascript" async
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
</script>"""

MATHJAX_CONFIG = """<script>
MathJax.Hub.Config({
  config: ["MMLorHTML.js"],
  extensions: ["tex2jax.js"],
  jax: ["input/TeX", "output/HTML-CSS", "output/NativeMML"],
  tex2jax: {
    inlineMath: [ ["\\(","\\)"] ],
    displayMath: [ ["\\[","\\]"] ],
    processEscapes: true,
    processEnvironments: true,
    ignoreClass: ".*|",
    processClass: "arithmatex"
  },
});
</script>"""

extension_config = {
    "pymdownx.arithmatex": {
        "generic": True,
        "preview": False,
    },
}

md = markdown.Markdown(extensions=extensions, extension_configs=extension_config,)


with open("test.md", mode="r") as f:
    content = f.read()
    html = md.convert(content)

with open("test.html", mode="w") as f:
    f.write(MATHJAX_SRC)
    f.write(MATHJAX_CONFIG)
    f.write(html)