#!/bin/bash

SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
EXAMPLES_NATIVE="${SCRIPT_DIRECTORY}/../gxformat2/examples/native"

wget -q https://raw.githubusercontent.com/galaxyproject/training-material/master/topics/assembly/tutorials/unicycler-assembly/workflows/unicycler.ga -O "${EXAMPLES_NATIVE}/real-unicycler-assembly.ga"
wget -q https://raw.githubusercontent.com/galaxyproject/training-material/master/topics/assembly/tutorials/ecoli_comparison/workflows/ecoli-comparison.ga -O "${EXAMPLES_NATIVE}/real-ecoli-comparison.ga"

