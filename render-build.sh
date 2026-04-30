#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Note: Render doesn't support apt-get in the build step for standard Python environments.
# To install Tesseract and Poppler, you should use Render's "Native Runtimes" with a custom Dockerfile,
# OR use a build script if they are pre-installed in certain images.
# However, for simple Python services, if they aren't pre-installed, you need a Dockerfile.
