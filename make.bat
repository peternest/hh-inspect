:: This is a batch file to run common actions.

@echo off
if "%~1"=="" goto help

if /I "%~1"=="format" goto format
if /I "%~1"=="check" goto check
if /I "%~1"=="test" goto test
if /I "%~1"=="run" goto run
if /I "%~1"=="update-deps" goto update-deps
if /I "%~1"=="clean" goto clean
if /I "%~1"=="help" goto help

echo Unknown command: %~1
goto help

:format
echo Formatting code...
uv run ruff format src/hh_inspect tests
goto end

:check
echo Running checks...
uv run ruff check src/hh_inspect tests
rem uv run pyright src/hh_inspect tests
rem .venv\Scripts\pyright --pythonpath .venv\Scripts\python src/hh_inspect tests
rem uv run mypy src --show-error-context --pretty
goto end

:test
echo Running tests...
uv run pytest tests
rem uv run pytest tests --cov=hh-inspect --cov-report=term-missing
goto end

:run
echo Running HH Inspector
uv run python src/hh_inspect/main.py
goto end

:update-deps
echo Updating dependencies...
uv sync -q
.venv\Scripts\python --version
.venv\Scripts\pytest --version
.venv\Scripts\ruff --version
goto end

:clean
if exist .mypy_cache rmdir /s /q .mypy_cache
if exist .ruff_cache rmdir /s /q .ruff_cache
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist dist rmdir /s /q dist
goto end

:help
echo Usage: .\make [format^|check^|test^|run^|update-deps^|clean^|help]
goto end

:end
