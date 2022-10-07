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
 * <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow</I><br>
 *
 * <BLOCKQUOTE>
 *
 * A Galaxy workflow description. This record corresponds to the description of a workflow that
 * should be executable on a Galaxy server that includes the contained tool definitions.
 *
 * <p>The workflows API or the user interface of Galaxy instances that are of version 19.09 or newer
 * should be able to import a document defining this record.
 *
 * <p>## A note about `label` field.
 *
 * <p>This is the name of the workflow in the Galaxy user interface. This is the mechanism that
 * users will primarily identify the workflow using. Legacy support - this may also be called 'name'
 * and Galaxy will consume the workflow document fine and treat this attribute correctly - however
 * in order to validate against this workflow definition schema the attribute should be called
 * `label`.
 *
 * </BLOCKQUOTE>
 */
public class GalaxyWorkflowImpl extends SaveableImpl implements GalaxyWorkflow {
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

  private String class_;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/class</I><br>
   */
  public String getClass_() {
    return this.class_;
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

  private java.util.List<Object> inputs;

  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#inputs</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the input parameters of the process. The process is ready to run when all required
   * input parameters are associated with concrete values. Input parameters include a schema for
   * each parameter which is used to validate the input object. It may also be used to build a user
   * interface for constructing the input object.
   *
   * <p>When accepting an input object, all input parameters must have a value. If an input
   * parameter is missing from the input object, it must be assigned a value of `null` (or the value
   * of `default` for that parameter, if provided) for the purposes of validation and evaluation of
   * expressions. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.List<Object> getInputs() {
    return this.inputs;
  }

  private java.util.List<Object> outputs;

  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#outputs</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the parameters representing the output of the process. May be used to generate and/or
   * validate the output object. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.List<Object> getOutputs() {
    return this.outputs;
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

  private java.util.List<Object> steps;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/steps</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The individual steps that make up the workflow. Each step is executed when all of its input
   * data links are fulfilled. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.List<Object> getSteps() {
    return this.steps;
  }

  private java.util.Optional<Report> report;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/report</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Workflow invocation report template. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<Report> getReport() {
    return this.report;
  }

  private java.util.Optional<java.util.List<String>> tags;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/tags</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Tags for the workflow. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<java.util.List<String>> getTags() {
    return this.tags;
  }

  private java.util.Optional<Object> creator;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/creator</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * Can be a schema.org Person (https://schema.org/Person) or Organization
   * (https://schema.org/Organization) entity *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<Object> getCreator() {
    return this.creator;
  }

  private java.util.Optional<String> license;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/license</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * Must be a valid license listed at https://spdx.org/licenses/ *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getLicense() {
    return this.license;
  }

  private java.util.Optional<String> release;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow/release</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * If listed should correspond to the release of the workflow in its source reposiory. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getRelease() {
    return this.release;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * GalaxyWorkflowImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public GalaxyWorkflowImpl(
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
      throw new ValidationException("GalaxyWorkflowImpl called on non-map");
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
    String class_;
    try {
      class_ =
          LoaderInstances.uri_StringInstance_False_True_None.loadField(
              __doc.get("class"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      class_ = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `class` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
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
    java.util.List<Object> inputs;
    try {
      inputs =
          LoaderInstances.idmap_inputs_array_of_WorkflowInputParameter.loadField(
              __doc.get("inputs"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      inputs = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `inputs` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    java.util.List<Object> outputs;
    try {
      outputs =
          LoaderInstances.idmap_outputs_array_of_WorkflowOutputParameter.loadField(
              __doc.get("outputs"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      outputs = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `outputs` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
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
    java.util.List<Object> steps;
    try {
      steps =
          LoaderInstances.idmap_steps_array_of_WorkflowStep.loadField(
              __doc.get("steps"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      steps = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `steps` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    java.util.Optional<Report> report;

    if (__doc.containsKey("report")) {
      try {
        report =
            LoaderInstances.optional_Report.loadField(
                __doc.get("report"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        report = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `report` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      report = null;
    }
    java.util.Optional<java.util.List<String>> tags;

    if (__doc.containsKey("tags")) {
      try {
        tags =
            LoaderInstances.optional_array_of_StringInstance.loadField(
                __doc.get("tags"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        tags = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `tags` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      tags = null;
    }
    java.util.Optional<Object> creator;

    if (__doc.containsKey("creator")) {
      try {
        creator =
            LoaderInstances.optional_AnyInstance.loadField(
                __doc.get("creator"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        creator = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `creator` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      creator = null;
    }
    java.util.Optional<String> license;

    if (__doc.containsKey("license")) {
      try {
        license =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("license"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        license = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `license` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      license = null;
    }
    java.util.Optional<String> release;

    if (__doc.containsKey("release")) {
      try {
        release =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("release"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        release = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `release` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      release = null;
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.id = (java.util.Optional<String>) id;
    this.label = (java.util.Optional<String>) label;
    this.doc = (Object) doc;
    this.inputs = (java.util.List<Object>) inputs;
    this.outputs = (java.util.List<Object>) outputs;
    this.uuid = (java.util.Optional<String>) uuid;
    this.class_ = (String) class_;
    this.steps = (java.util.List<Object>) steps;
    this.report = (java.util.Optional<Report>) report;
    this.tags = (java.util.Optional<java.util.List<String>>) tags;
    this.creator = (java.util.Optional<Object>) creator;
    this.license = (java.util.Optional<String>) license;
    this.release = (java.util.Optional<String>) release;
  }
}
