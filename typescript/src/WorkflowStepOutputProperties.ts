
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#WorkflowStepOutput
 *
 * Associate an output parameter of the underlying process with a workflow
 * parameter.  The workflow parameter (given in the `id` field) be may be used
 * as a `source` to connect with input parameters of other workflow steps, or
 * with an output parameter of the process.
 * 
 * A unique identifier for this workflow output parameter.  This is
 * the identifier to use in the `source` field of `WorkflowStepInput`
 * to connect the output value to downstream parameters.
 * 
 */
export interface WorkflowStepOutputProperties extends Internal.IdentifiedProperties {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * The unique identifier for this object.
   */
  id?: undefined | string
  add_tags?: undefined | Array<string>
  change_datatype?: undefined | string
  delete_intermediate_datasets?: undefined | boolean
  hide?: undefined | boolean
  remove_tags?: undefined | Array<string>
  rename?: undefined | string
  set_columns?: undefined | Array<string>
}