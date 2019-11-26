package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.LoaderInstances;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptions;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptionsBuilder;
import org.galaxyproject.gxformat2.v19_09.utils.SavableImpl;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

/**
 * Auto-generated class implementation for
 * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition</I><br>
 *
 * <BLOCKQUOTE>
 *
 * This field specifies the location of the step's node when rendered in the workflow editor.
 *
 * </BLOCKQUOTE>
 */
public class StepPositionImpl extends SavableImpl implements StepPosition {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private Float top;

  /**
   * Getter for property <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/top</I>
   * <br>
   *
   * <BLOCKQUOTE>
   *
   * Relative vertical position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  public Float getTop() {
    return this.top;
  }

  private Float left;

  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#StepPosition/left</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Relative horizontal position of the step's node when rendered in the workflow editor. *
   *
   * </BLOCKQUOTE>
   */
  public Float getLeft() {
    return this.left;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * StepPositionImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public StepPositionImpl(
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
      throw new ValidationException("StepPositionImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    Float top;
    try {
      top = LoaderInstances.FloatInstance.loadField(__doc.get("top"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      top = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `top` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    Float left;
    try {
      left =
          LoaderInstances.FloatInstance.loadField(__doc.get("left"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      left = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `left` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.top = (Float) top;
    this.left = (Float) left;
  }
}
