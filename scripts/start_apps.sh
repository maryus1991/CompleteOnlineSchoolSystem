#!/bin/bash

for app in accounts schools students teachers subjects content questions exams assignments live_classes progress grading communication payments subscriptions; do
    python ../manage.py startapp "$app"
done