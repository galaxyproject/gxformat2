
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow
 *
 * A Galaxy workflow description. This record corresponds to the description of a workflow that should be executable
 * on a Galaxy server that includes the contained tool definitions.
 * 
 * The workflows API or the user interface of Galaxy instances that are of version 19.09 or newer should be able to
 * import a document defining this record.
 * 
 * ## A note about `label` field.
 * 
 * This is the name of the workflow in the Galaxy user interface. This is the mechanism that
 * users will primarily identify the workflow using. Legacy support - this may also be called 'name' and Galaxy will
 * consume the workflow document fine and treat this attribute correctly - however in order to validate against this
 * workflow definition schema the attribute should be called `label`.
 * 
 */
export interface GalaxyWorkflowProperties extends Internal.ProcessProperties, Internal.HasUUIDProperties {
                    
  extensionFields?: Internal.Dictionary<any>

  /**
   * The unique identifier for this object.
   */
  id?: undefined | string
  class_?: string

  /**
   * A short, human-readable label of this object.
   */
  label?: undefined | string

  /**
   * A documentation string for this object, or an array of strings which should be concatenated.
   */
  doc?: undefined | string | Array<string>

  /**
   * Defines the input parameters of the process.  The process is ready to
   * run when all required input parameters are associated with concrete
   * values.  Input parameters include a schema for each parameter which is
   * used to validate the input object.  It may also be used to build a user
   * interface for constructing the input object.
   * 
   * When accepting an input object, all input parameters must have a value.
   * If an input parameter is missing from the input object, it must be
   * assigned a value of `null` (or the value of `default` for that
   * parameter, if provided) for the purposes of validation and evaluation
   * of expressions.
   * 
   */
  inputs: Array<Internal.WorkflowInputParameter>

  /**
   * Defines the parameters representing the output of the process.  May be
   * used to generate and/or validate the output object.
   * 
   */
  outputs: Array<Internal.WorkflowOutputParameter>

  /**
   * UUID uniquely representing this element.
   * 
   */
  uuid?: undefined | string

  /**
   * The individual steps that make up the workflow. Each step is executed when all of its
   * input data links are fulfilled.
   * 
   */
  steps: Array<Internal.WorkflowStep>

  /**
   * Workflow invocation report template.
   */
  report?: undefined | Internal.Report

  /**
   * Tags for the workflow.
   * 
   */
  tags?: Array<string> | undefined

  /**
   * Can be a schema.org Person (https://schema.org/Person) or Organization (https://schema.org/Organization) entity
   */
  creator?: undefined | any

  /**
   * Must be a valid license listed at https://spdx.org/licenses/
   */
  license?: undefined | string

  /**
   * If listed should correspond to the release of the workflow in its source reposiory.
   */
  release?: undefined | string
}