package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.LoaderInstances;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptions;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptionsBuilder;
import org.galaxyproject.gxformat2.v19_09.utils.SavableImpl;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

/**
 * Auto-generated class implementation for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep</I><br>
 *
 * <BLOCKQUOTE>
 *
 * Workflow step.
 *
 * </BLOCKQUOTE>
 */
public class WorkflowStepImpl extends SavableImpl implements WorkflowStep {
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
   * validate the output object. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<java.util.List<Object>> getOut() {
    return this.out;
  }

  private java.util.Optional<Object> state;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStep/state</I><br>
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

    if (id == null) {
      if (__docRoot != null) {
        id = java.util.Optional.of(__docRoot);
      } else {
        id = java.util.Optional.of("_:" + java.util.UUID.randomUUID().toString());
      }
    }
    __baseUri = (String) id.orElse(null);
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
                .uri_optional_array_of_union_of_StringInstance_or_WorkflowStepOutput_True_False_None
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
    this.in = (java.util.Optional<java.util.List<Object>>) in;
    this.out = (java.util.Optional<java.util.List<Object>>) out;
    this.state = (java.util.Optional<Object>) state;
    this.type = (java.util.Optional<WorkflowStepType>) type;
    this.run = (java.util.Optional<GalaxyWorkflow>) run;
  }
}
