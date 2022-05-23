#!/bin/bash

set -x
set -e

PROJECT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SKIP_JAVA=${SKIP_JAVA:-0}
SKIP_TYPESCRIPT=${SKIP_TYPESCRIPT:-0}
DIST_DIRECTORY="${PROJECT_DIRECTORY}/dist/schema"
rm -rf "${DIST_DIRECTORY}"
mkdir -p "${DIST_DIRECTORY}"
cp schema/*png "${DIST_DIRECTORY}"
curl https://raw.githubusercontent.com/jxtx/galaxy-bootstrap/master/dist/galaxy_bootstrap.min.css -o "$DIST_DIRECTORY/galaxy_bootstrap.min.css"

# Requires schema-salad-doc that recognizes --brandstyle and --brandinverse
for schema in "v19_09";
do
    cd schema/"$schema";
    python_schema_name=${schema//./_}
    schema-salad-tool --codegen python workflow.yml > "${PROJECT_DIRECTORY}/gxformat2/schema/${python_schema_name}.py"

    out="${DIST_DIRECTORY}/${schema}.html"
    schema-salad-doc \
        --brandstyle '<link rel="stylesheet" href="galaxy_bootstrap.min.css">' \
        --brandinverse \
        --brand '<img src="icon.png" />' \
        --brandlink '' \
        --only "https://galaxyproject.org/gxformat2/${schema}#WorkflowDoc" \
        --only "https://galaxyproject.org/gxformat2/${schema}#GalaxyWorkflow" \
        workflow.yml > "$out"

    if [ $SKIP_JAVA -eq 0 ]; then
        java_package="${PROJECT_DIRECTORY}/java"
        schema-salad-tool \
            --codegen java \
            --codegen-target "$java_package" \
            --codegen-examples examples \
            workflow.yml
        cd "$java_package"
        mvn test
        mvn javadoc:javadoc
        cd "$PROJECT_DIRECTORY"/schema/"$schema"
    fi
    if [ $SKIP_TYPESCRIPT -eq 0 ]; then
        ts_package="${PROJECT_DIRECTORY}/typescript"
        schema-salad-tool \
            --codegen typescript \
            --codegen-target "$ts_package" \
            --codegen-examples examples \
            workflow.yml
        cd "$ts_package"
        npm install
        npm test
        npm run doc
        cd "$PROJECT_DIRECTORY"/schema/"$schema"
    fi
done
