const path = require('path');
const fs = require('fs');
const reactDocgen = require('react-docgen');
const ReactDocGenMarkdownRenderer = require('react-docgen-markdown-renderer');
const componentPath = path.join(__dirname, 'src/components/emulator/emulator.js');
const renderer = new ReactDocGenMarkdownRenderer(/* constructor options object */);

fs.readFile(componentPath, (error, content) => {
  const documentationPath = path.basename(componentPath, path.extname(componentPath)) + renderer.extension;
  console.log(documentationPath)

  const doc = reactDocgen.parse(content);
  const md = renderer.render(
    /* The path to the component, used for linking to the file. */
    componentPath,
    /* The actual react-docgen AST */
    doc,
    /* Array of component ASTs that this component composes*/
    []);
  fs.writeFile(documentationPath, md, err => {
    if (err) {
      console.error(err)
      return
  }});
});
