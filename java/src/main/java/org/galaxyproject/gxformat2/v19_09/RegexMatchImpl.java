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
 * <I>https://galaxyproject.org/gxformat2/v19_09#RegexMatch</I><br>
 */
public class RegexMatchImpl extends SaveableImpl implements RegexMatch {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private String regex;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#RegexMatch/regex</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Check if a regular expression matches the value. A value is only valid if a match is found. *
   *
   * </BLOCKQUOTE>
   */
  public String getRegex() {
    return this.regex;
  }

  private String doc;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#RegexMatch/doc</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Message to provide to user if validator did not succeed. *
   *
   * </BLOCKQUOTE>
   */
  public String getDoc() {
    return this.doc;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * RegexMatchImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public RegexMatchImpl(
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
      throw new ValidationException("RegexMatchImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    String regex;
    try {
      regex =
          LoaderInstances.StringInstance.loadField(__doc.get("regex"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      regex = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `regex` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    String doc;
    try {
      doc = LoaderInstances.StringInstance.loadField(__doc.get("doc"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      doc = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `doc` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.regex = (String) regex;
    this.doc = (String) doc;
  }
}
