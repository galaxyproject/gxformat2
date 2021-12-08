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
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput</I><br>
 *
 * <BLOCKQUOTE>
 *
 * Associate an output parameter of the underlying process with a workflow parameter. The workflow
 * parameter (given in the `id` field) be may be used as a `source` to connect with input parameters
 * of other workflow steps, or with an output parameter of the process.
 *
 * <p>A unique identifier for this workflow output parameter. This is the identifier to use in the
 * `source` field of `WorkflowStepInput` to connect the output value to downstream parameters.
 *
 * </BLOCKQUOTE>
 */
public class WorkflowStepOutputImpl extends SaveableImpl implements WorkflowStepOutput {
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

  private java.util.Optional<java.util.List<String>> add_tags;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/add_tags</I><br>
   */
  public java.util.Optional<java.util.List<String>> getAdd_tags() {
    return this.add_tags;
  }

  private java.util.Optional<String> change_datatype;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/change_datatype</I><br>
   */
  public java.util.Optional<String> getChange_datatype() {
    return this.change_datatype;
  }

  private java.util.Optional<Boolean> delete_intermediate_datasets;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/delete_intermediate_datasets</I>
   * <br>
   */
  public java.util.Optional<Boolean> getDelete_intermediate_datasets() {
    return this.delete_intermediate_datasets;
  }

  private java.util.Optional<Boolean> hide;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/hide</I>
   * <br>
   */
  public java.util.Optional<Boolean> getHide() {
    return this.hide;
  }

  private java.util.Optional<java.util.List<String>> remove_tags;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/remove_tags</I><br>
   */
  public java.util.Optional<java.util.List<String>> getRemove_tags() {
    return this.remove_tags;
  }

  private java.util.Optional<String> rename;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/rename</I>
   * <br>
   */
  public java.util.Optional<String> getRename() {
    return this.rename;
  }

  private java.util.Optional<java.util.List<String>> set_columns;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput/set_columns</I><br>
   */
  public java.util.Optional<java.util.List<String>> getSet_columns() {
    return this.set_columns;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * WorkflowStepOutputImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public WorkflowStepOutputImpl(
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
      throw new ValidationException("WorkflowStepOutputImpl called on non-map");
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
    java.util.Optional<java.util.List<String>> add_tags;

    if (__doc.containsKey("add_tags")) {
      try {
        add_tags =
            LoaderInstances.optional_array_of_StringInstance.loadField(
                __doc.get("add_tags"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        add_tags = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `add_tags` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      add_tags = null;
    }
    java.util.Optional<String> change_datatype;

    if (__doc.containsKey("change_datatype")) {
      try {
        change_datatype =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("change_datatype"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        change_datatype = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `change_datatype` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      change_datatype = null;
    }
    java.util.Optional<Boolean> delete_intermediate_datasets;

    if (__doc.containsKey("delete_intermediate_datasets")) {
      try {
        delete_intermediate_datasets =
            LoaderInstances.optional_BooleanInstance.loadField(
                __doc.get("delete_intermediate_datasets"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        delete_intermediate_datasets =
            null; // won't be used but prevents compiler from complaining.
        final String __message = "the `delete_intermediate_datasets` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      delete_intermediate_datasets = null;
    }
    java.util.Optional<Boolean> hide;

    if (__doc.containsKey("hide")) {
      try {
        hide =
            LoaderInstances.optional_BooleanInstance.loadField(
                __doc.get("hide"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        hide = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `hide` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      hide = null;
    }
    java.util.Optional<java.util.List<String>> remove_tags;

    if (__doc.containsKey("remove_tags")) {
      try {
        remove_tags =
            LoaderInstances.optional_array_of_StringInstance.loadField(
                __doc.get("remove_tags"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        remove_tags = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `remove_tags` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      remove_tags = null;
    }
    java.util.Optional<String> rename;

    if (__doc.containsKey("rename")) {
      try {
        rename =
            LoaderInstances.optional_StringInstance.loadField(
                __doc.get("rename"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        rename = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `rename` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      rename = null;
    }
    java.util.Optional<java.util.List<String>> set_columns;

    if (__doc.containsKey("set_columns")) {
      try {
        set_columns =
            LoaderInstances.optional_array_of_StringInstance.loadField(
                __doc.get("set_columns"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        set_columns = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `set_columns` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      set_columns = null;
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.id = (java.util.Optional<String>) id;
    this.add_tags = (java.util.Optional<java.util.List<String>>) add_tags;
    this.change_datatype = (java.util.Optional<String>) change_datatype;
    this.delete_intermediate_datasets = (java.util.Optional<Boolean>) delete_intermediate_datasets;
    this.hide = (java.util.Optional<Boolean>) hide;
    this.remove_tags = (java.util.Optional<java.util.List<String>>) remove_tags;
    this.rename = (java.util.Optional<String>) rename;
    this.set_columns = (java.util.Optional<java.util.List<String>>) set_columns;
  }
}
