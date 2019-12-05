package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.LoaderInstances;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptions;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptionsBuilder;
import org.galaxyproject.gxformat2.v19_09.utils.SavableImpl;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

/**
 * Auto-generated class implementation for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter</I><br>
 */
public class WorkflowInputParameterImpl extends SavableImpl implements WorkflowInputParameter {
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

  private java.util.Optional<Object> default_;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#default</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The default value to use for this parameter if the parameter is missing from the input object,
   * or if the value of the parameter in the input object is `null`. Default values are applied
   * before evaluating expressions (e.g. dependent `valueFrom` fields). *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<Object> getDefault() {
    return this.default_;
  }

  private java.util.Optional<StepPosition> position;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><br>
   */
  public java.util.Optional<StepPosition> getPosition() {
    return this.position;
  }

  private java.util.Optional<GalaxyType> type;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specify valid types of data that may be assigned to this parameter. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<GalaxyType> getType() {
    return this.type;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * WorkflowInputParameterImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public WorkflowInputParameterImpl(
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
      throw new ValidationException("WorkflowInputParameterImpl called on non-map");
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
    java.util.Optional<Object> default_;

    if (__doc.containsKey("default")) {
      try {
        default_ =
            LoaderInstances.optional_AnyInstance.loadField(
                __doc.get("default"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        default_ = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `default` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      default_ = null;
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
    java.util.Optional<GalaxyType> type;

    if (__doc.containsKey("type")) {
      try {
        type =
            LoaderInstances.typedsl_optional_GalaxyType_2.loadField(
                __doc.get("type"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        type = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `type` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      type = null;
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.doc = (Object) doc;
    this.id = (java.util.Optional<String>) id;
    this.default_ = (java.util.Optional<Object>) default_;
    this.position = (java.util.Optional<StepPosition>) position;
    this.type = (java.util.Optional<GalaxyType>) type;
  }
}
