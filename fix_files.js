const fs = require('fs');
const path = require('path');

function fixFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      fixFiles(fullPath);
    } else {
      let content = fs.readFileSync(fullPath, 'utf8');
      // Remove the literal "\n" string that was accidentally appended
      if (content.endsWith('\\n')) {
        content = content.slice(0, -2) + '\n';
        fs.writeFileSync(fullPath, content, 'utf8');
      }
    }
  }
}

fixFiles(path.join(__dirname, 'frontend'));
console.log('Fixed trailing \\n in all files');
