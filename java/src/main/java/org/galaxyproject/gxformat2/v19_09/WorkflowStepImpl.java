// Copyright Common Workflow Language project contributors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.LoaderInstances;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptions;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptionsBuilder;
import org.galaxyproject.gxformat2.v19_09.utils.SaveableImpl;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

/**
 * Auto-generated class implementation for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep</I><br>
 *
 * <BLOCKQUOTE>
 *
 * This represents a non-input step a Galaxy Workflow.
 *
 * <p># A note about `state` and `tool_state` fields.
 *
 * <p>Only one or the other should be specified. These are two ways to represent the "state" of a
 * tool at this workflow step. Both are essentially maps from parameter names to parameter values.
 *
 * <p>`tool_state` is much more low-level and expects a flat dictionary with each value a JSON dump.
 * Nested tool structures such as conditionals and repeats should have all their values in the JSON
 * dumped string. In general `tool_state` may be present in workflows exported from Galaxy but
 * shouldn't be written by humans.
 *
 * <p>`state` can contained a typed map. Repeat values can be represented as YAML arrays. An
 * alternative to representing `state` this way is defining inputs with default values.
 *
 * </BLOCKQUOTE>
 */
public class WorkflowStepImpl extends SaveableImpl implements WorkflowStep {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private java.util.Optional<String> id;

  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Identified/id</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The unique identifier for this object. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getId() {
    return this.id;
  }

  private java.util.Optional<String> label;

  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Labeled/label</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A short, human-readable label of this object. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getLabel() {
    return this.label;
  }

  private Object doc;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#Documented/doc</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A documentation string for this object, or an array of strings which should be concatenated. *
   *
   * </BLOCKQUOTE>
   */
  public Object getDoc() {
    return this.doc;
  }

  private java.util.Optional<StepPosition> position;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><br>
   */
  public java.util.Optional<StepPosition> getPosition() {
    return this.position;
  }

  private java.util.Optional<String> tool_id;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_id</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The tool ID used to run this step of the workflow (e.g. 'cat1' or
   * 'toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset/4.0'). *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getTool_id() {
    return this.tool_id;
  }

  private java.util.Optional<ToolShedRepository> tool_shed_repository;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_shed_repository</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * The Galaxy Tool Shed repository that should be installed in order to use this tool. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<ToolShedRepository> getTool_shed_repository() {
    return this.tool_shed_repository;
  }

  private java.util.Optional<String> tool_version;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ReferencesTool/tool_version</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The tool version corresponding used to run this step of the workflow. For tool shed installed
   * tools, the ID generally uniquely specifies a version and this field is optional. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getTool_version() {
    return this.tool_version;
  }

  private java.util.Optional<String> errors;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepErrors/errors</I><br>
   *
   * <BLOCKQUOTE>
   *
   * During Galaxy export there may be some problem validating the tool state, tool used, etc.. that
   * will be indicated by this field. The Galaxy user should be warned of these problems before the
   * workflow can be used in Galaxy.
   *
   * <p>This field should not be used in human written Galaxy workflow files.
   *
   * <p>A typical problem is the referenced tool is not installed, this can be fixed by installed
   * the tool and re-saving the workflow and then re-exporting it. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getErrors() {
    return this.errors;
  }

  private java.util.Optional<String> uuid;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#HasUUID/uuid</I><br>
   *
   * <BLOCKQUOTE>
   *
   * UUID uniquely representing this element. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getUuid() {
    return this.uuid;
  }

  private java.util.Optional<java.util.List<Object>> in;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#in</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the input parameters of the workflow step. The process is ready to run when all
   * required input parameters are associated with concrete values. Input parameters include a
   * schema for each parameter which is used to validate the input object. It may also be used build
   * a user interface for constructing the input object. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<java.util.List<Object>> getIn() {
    return this.in;
  }

  private java.util.Optional<java.util.List<Object>> out;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#out</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the parameters representing the output of the process. May be used to generate and/or
   * validate the output object.
   *
   * <p>This can also be called 'outputs' for legacy reasons - but the resulting workflow document
   * is not a valid instance of this schema. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<java.util.List<Object>> getOut() {
    return this.out;
  }

  private java.util.Optional<Object> state;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#state</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Structured tool state. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<Object> getState() {
    return this.state;
  }

  private java.util.Optional<Object> tool_state;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#tool_state</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Unstructured tool state. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<Object> getTool_state() {
    return this.tool_state;
  }

  private java.util.Optional<WorkflowStepType> type;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Workflow step module's type (defaults to 'tool'). *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<WorkflowStepType> getType() {
    return this.type;
  }

  private java.util.Optional<GalaxyWorkflow> run;

  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#run</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specifies a subworkflow to run. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<GalaxyWorkflow> getRun() {
    return this.run;
  }

  private java.util.Optional<java.util.List<String>> runtime_inputs;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep/runtime_inputs</I><br>
   */
  public java.util.Optional<java.util.List<String>> getRuntime_inputs() {
    return this.runtime_inputs;
  }

  private java.util.Optional<String> when;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#when</I><br>
   *
   * <BLOCKQUOTE>
   *
   * If defined, only run the step when the expression evaluates to `true`. If `false` the step is
   * skipped. A skipped step produces a `null` on each output.
   *
   * <p>Expression should be an ecma5.1 expression. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getWhen() {
    return this.when;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * WorkflowStepImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public WorkflowStepImpl(
      final Object __doc_,
      final String __baseUri_,
      LoadingOptions __loadingOptions,
      final String __docRoot_) {
    super(__doc_, __baseUri_, __loadingOptions, __docRoot_);
    // Prefix plumbing variables with '__' to reduce likelihood of collision with
    // generated names.
    String __baseUri = __baseUri_;
    String __docRoot = __docRoot_;
    if (!(__doc_ instanceof java.util.Map)) {
      throw new ValidationException("WorkflowStepImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    java.util.Optional<String> id;

    if (__doc.containsKey("id")) {
      try {
        id =
            LoaderInstances.uri_optional_StringInstance_True_False_None.loadField(
                __doc.get("id"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        id = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `id` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      id = null;
    }

    Boolean __original_is_null = id == null;
    if (id == null) {
      if (__docRoot != null) {
        id = java.util.Optional.of(__docRoot);
      } else {
        id = java.util.Optional.of("_:" + java.util.UUID.randomUUID().toString());
      }
    }
    if (__original_is_null) {
      __baseUri = __baseUri_;
    } else {
      __baseUri = (String) id.orElse(null);
    }
    java.util.Optional<String> label;

    if (__doc.containsKey("label")) {
      try {
        label =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("label"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        label = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `label` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      label = null;
    }
    Object doc;

    if (__doc.containsKey("doc")) {
      try {
        doc =
            LoaderInstances.union_of_NullInstance_or_StringInstance_or_array_of_StringInstance
                .loadField(__doc.get("doc"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        doc = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `doc` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      doc = null;
    }
    java.util.Optional<StepPosition> position;

    if (__doc.containsKey("position")) {
      try {
        position =
            LoaderInstances.optional_StepPosition.loadField(
                __doc.get("position"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        position = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `position` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      position = null;
    }
    java.util.Optional<String> tool_id;

    if (__doc.containsKey("tool_id")) {
      try {
        tool_id =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("tool_id"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        tool_id = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `tool_id` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      tool_id = null;
    }
    java.util.Optional<ToolShedRepository> tool_shed_repository;

    if (__doc.containsKey("tool_shed_repository")) {
      try {
        tool_shed_repository =
            LoaderInstances.optional_ToolShedRepository.loadField(
                __doc.get("tool_shed_repository"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        tool_shed_repository = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `tool_shed_repository` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      tool_shed_repository = null;
    }
    java.util.Optional<String> tool_version;

    if (__doc.containsKey("tool_version")) {
      try {
        tool_version =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("tool_version"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        tool_version = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `tool_version` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      tool_version = null;
    }
    java.util.Optional<String> errors;

    if (__doc.containsKey("errors")) {
      try {
        errors =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("errors"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        errors = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `errors` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      errors = null;
    }
    java.util.Optional<String> uuid;

    if (__doc.containsKey("uuid")) {
      try {
        uuid =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("uuid"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        uuid = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `uuid` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      uuid = null;
    }
    java.util.Optional<java.util.List<Object>> in;

    if (__doc.containsKey("in")) {
      try {
        in =
            LoaderInstances.idmap_in_optional_array_of_WorkflowStepInput.loadField(
                __doc.get("in"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        in = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `in` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      in = null;
    }
    java.util.Optional<java.util.List<Object>> out;

    if (__doc.containsKey("out")) {
      try {
        out =
            LoaderInstances
                .idmap_out_optional_array_of_union_of_StringInstance_or_WorkflowStepOutput
                .loadField(__doc.get("out"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        out = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `out` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      out = null;
    }
    java.util.Optional<Object> state;

    if (__doc.containsKey("state")) {
      try {
        state =
            LoaderInstances.optional_AnyInstance.loadField(
                __doc.get("state"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        state = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `state` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      state = null;
    }
    java.util.Optional<Object> tool_state;

    if (__doc.containsKey("tool_state")) {
      try {
        tool_state =
            LoaderInstances.optional_AnyInstance.loadField(
                __doc.get("tool_state"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        tool_state = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `tool_state` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      tool_state = null;
    }
    java.util.Optional<WorkflowStepType> type;

    if (__doc.containsKey("type")) {
      try {
        type =
            LoaderInstances.typedsl_optional_WorkflowStepType_2.loadField(
                __doc.get("type"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        type = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `type` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      type = null;
    }
    java.util.Optional<GalaxyWorkflow> run;

    if (__doc.containsKey("run")) {
      try {
        run =
            LoaderInstances.uri_optional_GalaxyWorkflow_False_False_None.loadField(
                __doc.get("run"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        run = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `run` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      run = null;
    }
    java.util.Optional<java.util.List<String>> runtime_inputs;

    if (__doc.containsKey("runtime_inputs")) {
      try {
        runtime_inputs =
            LoaderInstances.optional_array_of_StringInstance.loadField(
                __doc.get("runtime_inputs"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        runtime_inputs = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `runtime_inputs` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      runtime_inputs = null;
    }
    java.util.Optional<String> when;

    if (__doc.containsKey("when")) {
      try {
        when =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("when"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        when = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `when` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      when = null;
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.id = (java.util.Optional<String>) id;
    this.label = (java.util.Optional<String>) label;
    this.doc = (Object) doc;
    this.position = (java.util.Optional<StepPosition>) position;
    this.tool_id = (java.util.Optional<String>) tool_id;
    this.tool_shed_repository = (java.util.Optional<ToolShedRepository>) tool_shed_repository;
    this.tool_version = (java.util.Optional<String>) tool_version;
    this.errors = (java.util.Optional<String>) errors;
    this.uuid = (java.util.Optional<String>) uuid;
    this.in = (java.util.Optional<java.util.List<Object>>) in;
    this.out = (java.util.Optional<java.util.List<Object>>) out;
    this.state = (java.util.Optional<Object>) state;
    this.tool_state = (java.util.Optional<Object>) tool_state;
    this.type = (java.util.Optional<WorkflowStepType>) type;
    this.run = (java.util.Optional<GalaxyWorkflow>) run;
    this.runtime_inputs = (java.util.Optional<java.util.List<String>>) runtime_inputs;
    this.when = (java.util.Optional<String>) when;
  }
}
