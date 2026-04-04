#!/bin/bash

set -x
set -e

PROJECT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USE_VENV=${USE_VENV:-"1"}
if [ "$USE_VENV" != "0" ]; then
    if [ -f "${PROJECT_DIRECTORY}/.venv/bin/activate" ]; then
        source "${PROJECT_DIRECTORY}/.venv/bin/activate"
    else
        echo "ERROR: USE_VENV=${USE_VENV} but ${PROJECT_DIRECTORY}/.venv/bin/activate not found" >&2
        exit 1
    fi
fi

GXFORMAT2_SCHEMA_BUILD_DRY_RUN=${GXFORMAT2_SCHEMA_BUILD_DRY_RUN:-"0"}
SCHEME_SOURCE_DIRECTORY="${PROJECT_DIRECTORY}/gxformat2/schema"
if [ "${GXFORMAT2_SCHEMA_BUILD_DRY_RUN}" = "1" ]; then
    SCHEME_SOURCE_DIRECTORY="$(mktemp -d -t gxformat2-schema.XXXXXX)"
    echo "GXFORMAT2_SCHEMA_BUILD_DRY_RUN=1; writing generated schemas to ${SCHEME_SOURCE_DIRECTORY}" >&2
fi
mkdir -p "${SCHEME_SOURCE_DIRECTORY}"
SKIP_JAVA=${SKIP_JAVA:-0}
SKIP_TYPESCRIPT=${SKIP_TYPESCRIPT:-0}
DIST_DIRECTORY="${PROJECT_DIRECTORY}/dist/schema"
rm -rf "${DIST_DIRECTORY}"
mkdir -p "${DIST_DIRECTORY}"
cp schema/*png "${DIST_DIRECTORY}"
cp schema/galaxy_docs.css "${DIST_DIRECTORY}/galaxy_docs.css"

# Requires schema-salad-doc that recognizes --brandstyle and --brandinverse
for schema in "v19_09";
do
    cd schema/"$schema";
    python_schema_name=${schema//./_}
    schema-salad-tool --codegen python workflow.yml > "${SCHEME_SOURCE_DIRECTORY}/${python_schema_name}.py"

    out="${DIST_DIRECTORY}/${schema}.html"
    schema-salad-doc \
        --brandstyle '<link rel="stylesheet" href="galaxy_docs.css">' \
        --brandinverse \
        --brand '<img src="icon.png" /> Galaxy Workflow Format 2' \
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

# Native workflow format schema
cd "${PROJECT_DIRECTORY}"/schema/native_v0_1
schema-salad-tool --codegen python workflow.yml > "${SCHEME_SOURCE_DIRECTORY}/native_v0_1.py"

out="${DIST_DIRECTORY}/native_v0_1.html"
schema-salad-doc \
    --brandstyle '<link rel="stylesheet" href="galaxy_docs.css">' \
    --brandinverse \
    --brand '<img src="icon.png" /> Galaxy Workflow Format 2' \
    --brandlink '' \
    --only "https://galaxyproject.org/gxformat2/native_v0_1#NativeWorkflowDoc" \
    --only "https://galaxyproject.org/gxformat2/native_v0_1#NativeGalaxyWorkflow" \
    workflow.yml > "$out"

# Pydantic models and enhanced docs (requires schema-salad-plus-pydantic)
# enhance-docs handles: pydantic:type overrides, pydantic:alias renames,
# and removing artificial class rows from documentRoot records.
SKIP_PYDANTIC=${SKIP_PYDANTIC:-0}
if [ $SKIP_PYDANTIC -eq 0 ]; then
    cd "${PROJECT_DIRECTORY}"
    schema-salad-plus-pydantic generate schema/v19_09/workflow.yml -o "${SCHEME_SOURCE_DIRECTORY}/gxformat2.py"
    schema-salad-plus-pydantic generate schema/v19_09/workflow.yml --strict -o "${SCHEME_SOURCE_DIRECTORY}/gxformat2_strict.py"
    schema-salad-plus-pydantic generate schema/native_v0_1/workflow.yml -o "${SCHEME_SOURCE_DIRECTORY}/native.py"
    schema-salad-plus-pydantic generate schema/native_v0_1/workflow.yml --strict -o "${SCHEME_SOURCE_DIRECTORY}/native_strict.py"
    schema-salad-plus-pydantic enhance-docs schema/native_v0_1/workflow.yml "${DIST_DIRECTORY}/native_v0_1.html"
else
    # Fallback post-processing without schema-salad-plus-pydantic
    sed -i.bak 's/format_version/format-version/g' "$out"
    python3 -c "
import re
html = open('$out').read()
html = re.sub(r'<div class=\"row responsive-table-row\">\s*\n<div[^>]*><code>class</code></div>\n.*?</div>\n</div>\n', '', html, flags=re.DOTALL)
open('$out', 'w').write(html)
"
    rm -f "$out.bak"
fi
