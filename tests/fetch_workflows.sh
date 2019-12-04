#!/bin/bash

TEST_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

wget -q https://raw.githubusercontent.com/galaxyproject/training-material/master/topics/assembly/tutorials/unicycler-assembly/workflows/unicycler.ga -O "${TEST_DIRECTORY}/unicycler.ga"
wget -q https://raw.githubusercontent.com/galaxyproject/training-material/master/topics/assembly/tutorials/ecoli_comparison/workflows/ecoli-comparison.ga -O "${TEST_DIRECTORY}/ecoli-comparison.ga"

