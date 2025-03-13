@echo off
echo Initializing ArchiTek FileBot Clone Project...
mkdir src
mkdir src\resources
mkdir src\resources\icons
mkdir src\resources\posters
mkdir docs
mkdir tests
mkdir logs

echo Creating placeholder files...
echo # Main application file > src\main.py
echo # GUI logic will be here > src\gui.py
echo # Handles renaming logic > src\renamer.py
echo # IMDB/TMDb integration > src\imdb_fetcher.py
echo # Subtitle fetching > src\subtitles.py
echo # Artwork fetching > src\artwork.py
echo # Configuration management > src\config.py
echo # Database handler > src\db.py
echo > logs\app.log
echo # API documentation will go here > docs\api_documentation.txt
echo # Development roadmap > docs\roadmap.txt
echo # Internal mechanics breakdown > docs\mechanics.txt
echo # UI/UX Design notes > docs\design_notes.txt
echo # Project setup instructions > docs\setup_guide.txt
echo # Git ignore rules > .gitignore
echo # Dependencies > requirements.txt
echo # Project ReadMe > README.md

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete! You can now start working on the project.
pause
