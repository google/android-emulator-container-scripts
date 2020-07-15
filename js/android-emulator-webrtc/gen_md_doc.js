/*
 * Copyright 2020 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
const path = require("path");
const fs = require("fs");
const reactDocgen = require("react-docgen");
const ReactDocGenMarkdownRenderer = require("react-docgen-markdown-renderer");
const componentPath = path.join(
  __dirname,
  "src/components/emulator/emulator.js"
);
const renderer = new ReactDocGenMarkdownRenderer();

fs.readFile(componentPath, (error, content) => {
  const documentationPath =
    path.basename(componentPath, path.extname(componentPath)) +
    renderer.extension;
  console.log(documentationPath);

  const doc = reactDocgen.parse(content);
  const md = renderer.render(componentPath, doc, []);
  fs.writeFile(documentationPath, md, (err) => {
    if (err) {
      console.error(err);
      return;
    }
  });
});
