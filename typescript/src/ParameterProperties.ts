
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://w3id.org/cwl/cwl#Parameter
 *
 * Define an input or output parameter to a process.
 * 
 */
export interface ParameterProperties extends Internal.LabeledProperties, Internal.DocumentedProperties, Internal.IdentifiedProperties {
                    
  /**
   * The unique identifier for this object.
   */
  id?: undefined | string

  /**
   * A short, human-readable label of this object.
   */
  label?: undefined | string

  /**
   * A documentation string for this object, or an array of strings which should be concatenated.
   */
  doc?: undefined | string | Array<string>
}