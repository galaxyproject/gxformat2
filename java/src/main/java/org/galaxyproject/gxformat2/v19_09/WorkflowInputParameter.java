package org.galaxyproject.gxformat2.v19_09;

import org.galaxyproject.gxformat2.v19_09.utils.Savable;

/**
 * Auto-generated interface for
 * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter</I><br>
 * This interface is implemented by {@link WorkflowInputParameterImpl}<br>
 */
public interface WorkflowInputParameter extends InputParameter, HasStepPosition, Savable {
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Identified/id</I><br>
   *
   * <BLOCKQUOTE>
   *
   * The unique identifier for this object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getId();
  /**
   * Getter for property <I>https://w3id.org/cwl/cwl#Labeled/label</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A short, human-readable label of this object. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getLabel();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#Documented/doc</I><br>
   *
   * <BLOCKQUOTE>
   *
   * A documentation string for this object, or an array of strings which should be concatenated. *
   *
   * </BLOCKQUOTE>
   */
  Object getDoc();
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
  java.util.Optional<Object> getDefault();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/gxformat2common#HasStepPosition/position</I><br>
   */
  java.util.Optional<StepPosition> getPosition();
  /**
   * Getter for property <I>https://w3id.org/cwl/salad#type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specify valid types of data that may be assigned to this parameter. *
   *
   * </BLOCKQUOTE>
   */
  Object getType();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter/optional</I><br>
   *
   * <BLOCKQUOTE>
   *
   * If set to true, `WorkflowInputParameter` is not required to submit the workflow. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<Boolean> getOptional();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter/format</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Specify datatype extension for valid input datasets. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<java.util.List<Object>> getFormat();
  /**
   * Getter for property
   * <I>https://galaxyproject.org/gxformat2/v19_09#WorkflowInputParameter/collection_type</I><br>
   *
   * <BLOCKQUOTE>
   *
   * Collection type (defaults to `list` if `type` is `collection`). Nested collection types are
   * separated with colons, e.g. `list:list:paired`. *
   *
   * </BLOCKQUOTE>
   */
  java.util.Optional<String> getCollection_type();
}
