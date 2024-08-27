
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#WorkflowTextParameter
 */
export interface WorkflowTextParameterProperties extends Internal.BaseInputParameterProperties {
                    
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
   * The default value to use for this parameter if the parameter is missing
   * from the input object, or if the value of the parameter in the input
   * object is `null`.  Default values are applied before evaluating expressions
   * (e.g. dependent `valueFrom` fields).
   * 
   */
  default_?: undefined | any
  position?: undefined | Internal.StepPosition

  /**
   * If set to true, `WorkflowInputParameter` is not required to submit the workflow.
   * 
   */
  optional?: boolean | undefined
  type: Internal.GalaxyTextType | Array<Internal.WorkflowTextParameter>

  /**
   * Apply one more validators to the input value. Input is valid if all validators succeed.
   */
  validators?: undefined | Array<Internal.TextValidators>
}