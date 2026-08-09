const fs = require('fs');
const path = require('path');
const root = path.join(__dirname, '..');
const src = path.join(root, 'node_modules', '@fortawesome', 'fontawesome-free');
const destCss = path.join(root, 'static', 'vendor', 'fontawesome');
const destFonts = path.join(root, 'static', 'vendor', 'webfonts');
fs.rmSync(destCss, { recursive: true, force: true });
fs.rmSync(destFonts, { recursive: true, force: true });
fs.mkdirSync(destCss, { recursive: true });
fs.mkdirSync(destFonts, { recursive: true });
fs.copyFileSync(path.join(src, 'css', 'all.min.css'), path.join(destCss, 'all.min.css'));
for (const file of fs.readdirSync(path.join(src, 'webfonts'))) {
  fs.copyFileSync(path.join(src, 'webfonts', file), path.join(destFonts, file));
}
console.log('FontAwesome copiado a static/vendor/');
