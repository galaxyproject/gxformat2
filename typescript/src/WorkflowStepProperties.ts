
import * as Internal from './util/Internal'


/**
 * Auto-generated interface for https://galaxyproject.org/gxformat2/v19_09#WorkflowStep
 *
 * This represents a non-input step a Galaxy Workflow.
 * 
 * # A note about `state` and `tool_state` fields.
 * 
 * Only one or the other should be specified. These are two ways to represent the "state"
 * of a tool at this workflow step. Both are essentially maps from parameter names to
 * parameter values.
 * 
 * `tool_state` is much more low-level and expects a flat dictionary with each value a JSON
 * dump. Nested tool structures such as conditionals and repeats should have all their values
 * in the JSON dumped string. In general `tool_state` may be present in workflows exported from
 * Galaxy but shouldn't be written by humans.
 * 
 * `state` can contained a typed map. Repeat values can be represented as YAML arrays. An alternative
 * to representing `state` this way is defining inputs with default values.
 * 
 */
export interface WorkflowStepProperties extends Internal.IdentifiedProperties, Internal.LabeledProperties, Internal.DocumentedProperties, Internal.HasStepPositionProperties, Internal.ReferencesToolProperties, Internal.HasStepErrorsProperties, Internal.HasUUIDProperties {
                    
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
  position?: undefined | Internal.StepPosition

  /**
   * The tool ID used to run this step of the workflow (e.g. 'cat1' or 'toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset/4.0').
   * 
   */
  tool_id?: undefined | string

  /**
   * The Galaxy Tool Shed repository that should be installed in order to use this tool.
   * 
   */
  tool_shed_repository?: undefined | Internal.ToolShedRepository

  /**
   * The tool version corresponding used to run this step of the workflow. For tool shed installed tools, the ID generally uniquely specifies a version
   * and this field is optional.
   * 
   */
  tool_version?: undefined | string

  /**
   * During Galaxy export there may be some problem validating the tool state, tool used, etc..
   * that will be indicated by this field. The Galaxy user should be warned of these problems before
   * the workflow can be used in Galaxy.
   * 
   * This field should not be used in human written Galaxy workflow files.
   * 
   * A typical problem is the referenced tool is not installed, this can be fixed by installed the tool
   * and re-saving the workflow and then re-exporting it.
   * 
   */
  errors?: undefined | string

  /**
   * UUID uniquely representing this element.
   * 
   */
  uuid?: undefined | string

  /**
   * Defines the input parameters of the workflow step.  The process is ready to
   * run when all required input parameters are associated with concrete
   * values.  Input parameters include a schema for each parameter which is
   * used to validate the input object.  It may also be used build a user
   * interface for constructing the input object.
   * 
   */
  in_?: undefined | Array<Internal.WorkflowStepInput>

  /**
   * Defines the parameters representing the output of the process.  May be
   * used to generate and/or validate the output object.
   * 
   * This can also be called 'outputs' for legacy reasons - but the resulting
   * workflow document is not a valid instance of this schema.
   * 
   */
  out?: Array<string | Internal.WorkflowStepOutput> | undefined

  /**
   * Structured tool state.
   * 
   */
  state?: undefined | any

  /**
   * Unstructured tool state.
   * 
   */
  tool_state?: undefined | any

  /**
   * Workflow step module's type (defaults to 'tool').
   * 
   */
  type?: undefined | Internal.WorkflowStepType

  /**
   * Specifies a subworkflow to run.
   * 
   */
  run?: undefined | Internal.GalaxyWorkflow
  runtime_inputs?: undefined | Array<string>

  /**
   * If defined, only run the step when the expression evaluates to
   * `true`.  If `false` the step is skipped.  A skipped step
   * produces a `null` on each output.
   * 
   * Expression should be an ecma5.1 expression.
   * 
   */
  when?: undefined | string
}