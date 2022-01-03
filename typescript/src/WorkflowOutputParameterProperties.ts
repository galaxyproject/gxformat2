
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter
 *
 * Describe an output parameter of a workflow.  The parameter must be
 * connected to one parameter defined in the workflow that
 * will provide the value of the output parameter. It is legal to
 * connect a WorkflowInputParameter to a WorkflowOutputParameter.
 * 
 */
export interface WorkflowOutputParameterProperties extends Internal.OutputParameterProperties {
                    
  extensionFields?: Internal.Dictionary<any>

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

  /**
   * Specifies workflow parameter that supply the value of to
   * the output parameter.
   * 
   */
  outputSource?: undefined | string

  /**
   * Specify valid types of data that may be assigned to this parameter.
   * 
   */
  type?: undefined | Internal.GalaxyType
}