#!/bin/bash
find . | grep -E &#34;(__pycache__|\.pyc|\.pyo$)&#34; | xargs rm -rf