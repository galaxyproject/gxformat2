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
 * Auto-generated class implementation for <I>https://galaxyproject.org/gxformat2/v19_09#MinMax</I>
 * <br>
 */
public class MinMaxImpl extends SaveableImpl implements MinMax {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private Object min;

  /** Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#MinMax/min</I><br> */
  public Object getMin() {
    return this.min;
  }

  private Object max;

  /** Getter for property <I>https://galaxyproject.org/gxformat2/v19_09#MinMax/max</I><br> */
  public Object getMax() {
    return this.max;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * MinMaxImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public MinMaxImpl(
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
      throw new ValidationException("MinMaxImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    Object min;

    if (__doc.containsKey("min")) {
      try {
        min =
            LoaderInstances.union_of_IntegerInstance_or_DoubleInstance_or_NullInstance.loadField(
                __doc.get("min"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        min = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `min` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      min = null;
    }
    Object max;

    if (__doc.containsKey("max")) {
      try {
        max =
            LoaderInstances.union_of_IntegerInstance_or_DoubleInstance_or_NullInstance.loadField(
                __doc.get("max"), __baseUri, __loadingOptions);
      } catch (ValidationException e) {
        max = null; // won't be used but prevents compiler from complaining.
        final String __message = "the `max` field is not valid because:";
        __errors.add(new ValidationException(__message, e));
      }

    } else {
      max = null;
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.min = (Object) min;
    this.max = (Object) max;
  }
}
