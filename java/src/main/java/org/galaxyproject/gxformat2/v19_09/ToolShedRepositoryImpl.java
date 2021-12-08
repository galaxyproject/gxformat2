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
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository</I><br>
 */
public class ToolShedRepositoryImpl extends SaveableImpl implements ToolShedRepository {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private String name;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/name</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The name of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  public String getName() {
    return this.name;
  }

  private String changeset_revision;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/changeset_revision</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * The revision of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  public String getChangeset_revision() {
    return this.changeset_revision;
  }

  private String owner;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/owner</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The owner of the tool shed repository this tool can be found in. *
   *
   * </BLOCKQUOTE>
   */
  public String getOwner() {
    return this.owner;
  }

  private String tool_shed;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#ToolShedRepository/tool_shed</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The URI of the tool shed containing the repository this tool can be found in - typically this
   * should be toolshed.g2.bx.psu.edu. *
   *
   * </BLOCKQUOTE>
   */
  public String getTool_shed() {
    return this.tool_shed;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * ToolShedRepositoryImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public ToolShedRepositoryImpl(
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
      throw new ValidationException("ToolShedRepositoryImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    String name;

    if (__doc.containsKey("name")) {
      try {
        name =
            LoaderInstances.uri_StringInstance_True_False_None.loadField(
                __doc.get("name"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        name = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `name` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      name = null;
    }

    if (name == null) {
      if (__docRoot != null) {
        name = __docRoot;
      } else {
        throw new ValidationException("Missing name");
      }
    }
    __baseUri = (String) name;
    String changeset_revision;
    try {
      changeset_revision =
          LoaderInstances.StringInstance.loadField(
              __doc.get("changeset_revision"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      changeset_revision = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `changeset_revision` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    String owner;
    try {
      owner =
          LoaderInstances.StringInstance.loadField(__doc.get("owner"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      owner = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `owner` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    String tool_shed;
    try {
      tool_shed =
          LoaderInstances.StringInstance.loadField(
              __doc.get("tool_shed"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      tool_shed = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `tool_shed` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.changeset_revision = (String) changeset_revision;
    this.name = (String) name;
    this.owner = (String) owner;
    this.tool_shed = (String) tool_shed;
  }
}
