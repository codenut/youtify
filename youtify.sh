#!/bin/bash

env $(cat .env | xargs) python main.py
