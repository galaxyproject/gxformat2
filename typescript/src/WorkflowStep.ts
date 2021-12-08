
import {
  Dictionary,
  expandUrl,
  loadField,
  LoaderInstances,
  LoadingOptions,
  Saveable,
  ValidationException,
  prefixUrl,
  save,
  saveRelativeUri
} from './util/Internal'
import { v4 as uuidv4 } from 'uuid'
import * as Internal from './util/Internal'


/**
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#WorkflowStep
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
export class WorkflowStep extends Saveable implements Internal.WorkflowStepProperties {
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


  constructor ({loadingOptions, extensionFields, id, label, doc, position, tool_id, tool_shed_repository, tool_version, errors, uuid, in_, out, state, tool_state, type, run, runtime_inputs, when} : {loadingOptions?: LoadingOptions} & Internal.WorkflowStepProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.id = id
    this.label = label
    this.doc = doc
    this.position = position
    this.tool_id = tool_id
    this.tool_shed_repository = tool_shed_repository
    this.tool_version = tool_version
    this.errors = errors
    this.uuid = uuid
    this.in_ = in_
    this.out = out
    this.state = state
    this.tool_state = tool_state
    this.type = type
    this.run = run
    this.runtime_inputs = runtime_inputs
    this.when = when
  }

  /**
   * Used to construct instances of {@link WorkflowStep }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link WorkflowStep }
   * @throws {@link ValidationException}    If the document fragment is not a
   *                                        {@link Dictionary} or validation of fields fails.
   */
  static override async fromDoc (__doc: any, baseuri: string, loadingOptions: LoadingOptions,
    docRoot?: string): Promise<Saveable> {
    const _doc = Object.assign({}, __doc)
    const __errors: ValidationException[] = []
            
    let id
    if ('id' in _doc) {
      try {
        id = await loadField(_doc.id, LoaderInstances.uriunionOfundefinedtypeOrstrtypeTrueFalseNone,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `id` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const originalidIsUndefined = (id === undefined)
    if (originalidIsUndefined ) {
      if (docRoot != null) {
        id = docRoot
      } else {
        id = "_" + uuidv4()
      }
    } else {
      baseuri = id as string
    }
            
    let label
    if ('label' in _doc) {
      try {
        label = await loadField(_doc.label, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `label` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let doc
    if ('doc' in _doc) {
      try {
        doc = await loadField(_doc.doc, LoaderInstances.unionOfundefinedtypeOrstrtypeOrarrayOfstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `doc` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let position
    if ('position' in _doc) {
      try {
        position = await loadField(_doc.position, LoaderInstances.unionOfundefinedtypeOrStepPositionLoader,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `position` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let tool_id
    if ('tool_id' in _doc) {
      try {
        tool_id = await loadField(_doc.tool_id, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `tool_id` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let tool_shed_repository
    if ('tool_shed_repository' in _doc) {
      try {
        tool_shed_repository = await loadField(_doc.tool_shed_repository, LoaderInstances.unionOfundefinedtypeOrToolShedRepositoryLoader,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `tool_shed_repository` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let tool_version
    if ('tool_version' in _doc) {
      try {
        tool_version = await loadField(_doc.tool_version, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `tool_version` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let errors
    if ('errors' in _doc) {
      try {
        errors = await loadField(_doc.errors, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `errors` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let uuid
    if ('uuid' in _doc) {
      try {
        uuid = await loadField(_doc.uuid, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `uuid` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let in_
    if ('in' in _doc) {
      try {
        in_ = await loadField(_doc.in, LoaderInstances.idmapin_unionOfundefinedtypeOrarrayOfWorkflowStepInputLoader,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `in` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let out
    if ('out' in _doc) {
      try {
        out = await loadField(_doc.out, LoaderInstances.idmapoutunionOfarrayOfunionOfstrtypeOrWorkflowStepOutputLoaderOrundefinedtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `out` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let state
    if ('state' in _doc) {
      try {
        state = await loadField(_doc.state, LoaderInstances.unionOfundefinedtypeOranyType,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `state` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let tool_state
    if ('tool_state' in _doc) {
      try {
        tool_state = await loadField(_doc.tool_state, LoaderInstances.unionOfundefinedtypeOranyType,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `tool_state` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let type
    if ('type' in _doc) {
      try {
        type = await loadField(_doc.type, LoaderInstances.typedslunionOfundefinedtypeOrWorkflowStepTypeLoader2,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `type` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let run
    if ('run' in _doc) {
      try {
        run = await loadField(_doc.run, LoaderInstances.uriunionOfundefinedtypeOrGalaxyWorkflowLoaderFalseFalseNone,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `run` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let runtime_inputs
    if ('runtime_inputs' in _doc) {
      try {
        runtime_inputs = await loadField(_doc.runtime_inputs, LoaderInstances.unionOfundefinedtypeOrarrayOfstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `runtime_inputs` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let when
    if ('when' in _doc) {
      try {
        when = await loadField(_doc.when, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `when` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!WorkflowStep.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`id\`,\`label\`,\`doc\`,\`position\`,\`tool_id\`,\`tool_shed_repository\`,\`tool_version\`,\`errors\`,\`uuid\`,\`in\`,\`out\`,\`state\`,\`tool_state\`,\`type\`,\`run\`,\`runtime_inputs\`,\`when\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'WorkflowStep'", __errors)
    }

    const schema = new WorkflowStep({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      id: id,
      label: label,
      doc: doc,
      position: position,
      tool_id: tool_id,
      tool_shed_repository: tool_shed_repository,
      tool_version: tool_version,
      errors: errors,
      uuid: uuid,
      in_: in_,
      out: out,
      state: state,
      tool_state: tool_state,
      type: type,
      run: run,
      runtime_inputs: runtime_inputs,
      when: when
    })
    return schema
  }
        
  save (top: boolean = false, baseUrl: string = '', relativeUris: boolean = true)
  : Dictionary<any> {
    const r: Dictionary<any> = {}
    for (const ef in this.extensionFields) {
      r[prefixUrl(ef, this.loadingOptions.vocab)] = this.extensionFields.ef
    }

    if (this.id != null) {
      const u = saveRelativeUri(this.id, baseUrl, true,
                                relativeUris, undefined)
      if (u != null) {
        r.id = u
      }
    }
                
    if (this.label != null) {
      r.label = save(this.label, false, this.id, relativeUris)
    }
                
    if (this.doc != null) {
      r.doc = save(this.doc, false, this.id, relativeUris)
    }
                
    if (this.position != null) {
      r.position = save(this.position, false, this.id, relativeUris)
    }
                
    if (this.tool_id != null) {
      r.tool_id = save(this.tool_id, false, this.id, relativeUris)
    }
                
    if (this.tool_shed_repository != null) {
      r.tool_shed_repository = save(this.tool_shed_repository, false, this.id, relativeUris)
    }
                
    if (this.tool_version != null) {
      r.tool_version = save(this.tool_version, false, this.id, relativeUris)
    }
                
    if (this.errors != null) {
      r.errors = save(this.errors, false, this.id, relativeUris)
    }
                
    if (this.uuid != null) {
      r.uuid = save(this.uuid, false, this.id, relativeUris)
    }
                
    if (this.in_ != null) {
      r.in = save(this.in_, false, this.id, relativeUris)
    }
                
    if (this.out != null) {
      r.out = save(this.out, false, this.id, relativeUris)
    }
                
    if (this.state != null) {
      r.state = save(this.state, false, this.id, relativeUris)
    }
                
    if (this.tool_state != null) {
      r.tool_state = save(this.tool_state, false, this.id, relativeUris)
    }
                
    if (this.type != null) {
      r.type = save(this.type, false, this.id, relativeUris)
    }
                
    if (this.run != null) {
      const u = saveRelativeUri(this.run, this.id, false,
                                relativeUris, undefined)
      if (u != null) {
        r.run = u
      }
    }
                
    if (this.runtime_inputs != null) {
      r.runtime_inputs = save(this.runtime_inputs, false, this.id, relativeUris)
    }
                
    if (this.when != null) {
      r.when = save(this.when, false, this.id, relativeUris)
    }
                
    if (top) {
      if (this.loadingOptions.namespaces != null) {
        r.$namespaces = this.loadingOptions.namespaces
      }
      if (this.loadingOptions.schemas != null) {
        r.$schemas = this.loadingOptions.schemas
      }
    }
    return r
  }
            
  static attr: Set<string> = new Set(['id','label','doc','position','tool_id','tool_shed_repository','tool_version','errors','uuid','in','out','state','tool_state','type','run','runtime_inputs','when'])
}
