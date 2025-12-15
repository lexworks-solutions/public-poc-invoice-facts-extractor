#!/bin/bash

function install() {
  sudo apt update -y
  sudo apt install -y \
    tesseract-ocr \
    libtesseract-dev
}

function main() {
  install
}

main