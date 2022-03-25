
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#WorkflowStepInput
 *
 * TODO:
 * 
 */
export interface WorkflowStepInputProperties extends Internal.IdentifiedProperties, Internal.SinkProperties, Internal.LabeledProperties {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * The unique identifier for this object.
   */
  id?: undefined | string

  /**
   * Specifies one or more workflow parameters that will provide input to
   * the underlying step parameter.
   * 
   */
  source?: undefined | string | Array<string>

  /**
   * A short, human-readable label of this object.
   */
  label?: undefined | string

  /**
   * The default value for this parameter to use if either there is no
   * `source` field, or the value produced by the `source` is `null`.  The
   * default must be applied prior to scattering or evaluating `valueFrom`.
   * 
   */
  default_?: undefined | any
}