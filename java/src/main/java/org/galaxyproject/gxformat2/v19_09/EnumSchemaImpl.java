package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.LoaderInstances;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptions;
import org.galaxyproject.gxformat2.v19_09.utils.LoadingOptionsBuilder;
import org.galaxyproject.gxformat2.v19_09.utils.SavableImpl;
import org.galaxyproject.gxformat2.v19_09.utils.ValidationException;

/**
 * Auto-generated class implementation for <I>https://w3id.org/cwl/salad#EnumSchema</I><br>
 *
 * <BLOCKQUOTE>
 *
 * Define an enumerated type.
 *
 * </BLOCKQUOTE>
 */
public class EnumSchemaImpl extends SavableImpl implements EnumSchema {
  private LoadingOptions loadingOptions_ = new LoadingOptionsBuilder().build();
  private java.util.Map<String, Object> extensionFields_ = new java.util.HashMap<String, Object>();

  private java.util.List<Object> symbols;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#symbols</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Defines the set of valid symbols. *
   *
   * </BLOCKQUOTE>
   */
  public java.util.List<Object> getSymbols() {
    return this.symbols;
  }

  private enum_d961d79c225752b9fadb617367615ab176b47d77 type;

  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Must be `enum` *
   *
   * </BLOCKQUOTE>
   */
  public enum_d961d79c225752b9fadb617367615ab176b47d77 getType() {
    return this.type;
  }

  /**
   * Used by {@link org.galaxyproject.gxformat2.v19_09.utils.RootLoader} to construct instances of
   * EnumSchemaImpl.
   *
   * @param __doc_ Document fragment to load this record object from (presumably a {@link
   *     java.util.Map}).
   * @param __baseUri_ Base URI to generate child document IDs against.
   * @param __loadingOptions Context for loading URIs and populating objects.
   * @param __docRoot_ ID at this position in the document (if available) (maybe?)
   * @throws ValidationException If the document fragment is not a {@link java.util.Map} or
   *     validation of fields fails.
   */
  public EnumSchemaImpl(
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
      throw new ValidationException("EnumSchemaImpl called on non-map");
    }
    final java.util.Map<String, Object> __doc = (java.util.Map<String, Object>) __doc_;
    final java.util.List<ValidationException> __errors =
        new java.util.ArrayList<ValidationException>();
    if (__loadingOptions != null) {
      this.loadingOptions_ = __loadingOptions;
    }
    java.util.List<Object> symbols;
    try {
      symbols =
          LoaderInstances.uri_array_of_StringInstance_True_False_None.loadField(
              __doc.get("symbols"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      symbols = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `symbols` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    enum_d961d79c225752b9fadb617367615ab176b47d77 type;
    try {
      type =
          LoaderInstances.typedsl_enum_d961d79c225752b9fadb617367615ab176b47d77_2.loadField(
              __doc.get("type"), __baseUri, __loadingOptions);
    } catch (ValidationException e) {
      type = null; // won't be used but prevents compiler from complaining.
      final String __message = "the `type` field is not valid because:";
      __errors.add(new ValidationException(__message, e));
    }
    if (!__errors.isEmpty()) {
      throw new ValidationException("Trying 'RecordField'", __errors);
    }
    this.symbols = (java.util.List<Object>) symbols;
    this.type = (enum_d961d79c225752b9fadb617367615ab176b47d77) type;
  }
}
