import shutil
import os

print("Backing up Original Mock Data...")
shutil.copy("js/content-data.js", "js/content-data.js.bak")
shutil.copy("js/articles-data.js", "js/articles-data.js.bak")
print("Backup complete!")
