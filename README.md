# Cura Conan recipes

WIP

# dev notes

to develop your package go into the recipe folder and run:
```bash
conan source . -sf tmp/src
conan install . -if tmp/bld --build=missing -pr cura_msvc
conan build . --source-folder=tmp/src --build-folder=tmp/bld -pr cura_msvc
conan package . --source-folder=tmp/src --build-folder=tmp/bld --package-folder=tmp/pkg
conan export-pkg . sip/testing --source-folder=tmp/src --build-folder=tmp/bld
```