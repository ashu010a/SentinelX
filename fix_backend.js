const fs = require('fs');
const path = require('path');

function fixFiles(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'venv' || entry.name === '__pycache__') continue; // Skip virtual env
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      fixFiles(fullPath);
    } else {
      let content = fs.readFileSync(fullPath, 'utf8');
      if (content.endsWith('\\n')) {
        content = content.slice(0, -2) + '\n';
        fs.writeFileSync(fullPath, content, 'utf8');
      }
    }
  }
}

fixFiles(path.join(__dirname, 'backend'));
console.log('Fixed trailing \\n in backend files');
