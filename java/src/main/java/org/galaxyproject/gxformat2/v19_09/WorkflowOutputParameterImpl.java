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
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter</I><br>
 *
 * <BLOCKQUOTE>
 *
 * Describe an output parameter of a workflow. The parameter must be connected to one parameter
 * defined in the workflow that will provide the value of the output parameter. It is legal to
 * connect a WorkflowInputParameter to a WorkflowOutputParameter.
 *
 * </BLOCKQUOTE>
 */
public class WorkflowOutputParameterImpl extends SaveableImpl implements WorkflowOutputParameter {
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

  private java.util.Optional<String> outputSource;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter/outputSource</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specifies workflow parameter that supply the value of to the output parameter. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.Optional<String> getOutputSource() {
    return this.outputSource;
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
   * WorkflowOutputParameterImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public WorkflowOutputParameterImpl(
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
      throw new ValidationException("WorkflowOutputParameterImpl called on non-map");
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
    java.util.Optional<String> outputSource;

    if (__doc.containsKey("outputSource")) {
      try {
        outputSource =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("outputSource"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        outputSource = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `outputSource` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      outputSource = null;
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
    this.label = (java.util.Optional<String>) label;
    this.doc = (Object) doc;
    this.id = (java.util.Optional<String>) id;
    this.outputSource = (java.util.Optional<String>) outputSource;
    this.type = (java.util.Optional<GalaxyType>) type;
  }
}
