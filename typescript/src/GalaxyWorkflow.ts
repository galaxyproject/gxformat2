
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#GalaxyWorkflow
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
export class GalaxyWorkflow extends Saveable implements Internal.GalaxyWorkflowProperties {
  extensionFields?: Internal.Dictionary<any>

  /**
   * The unique identifier for this object.
   */
  id?: undefined | string
  class_: string

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


  constructor ({loadingOptions, extensionFields, id, class_ = 'GalaxyWorkflow', label, doc, inputs, outputs, uuid, steps, report, tags, creator, license, release} : {loadingOptions?: LoadingOptions} & Internal.GalaxyWorkflowProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.id = id
    this.class_ = class_
    this.label = label
    this.doc = doc
    this.inputs = inputs
    this.outputs = outputs
    this.uuid = uuid
    this.steps = steps
    this.report = report
    this.tags = tags
    this.creator = creator
    this.license = license
    this.release = release
  }

  /**
   * Used to construct instances of {@link GalaxyWorkflow }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link GalaxyWorkflow }
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
            
    let class_
    try {
      class_ = await loadField(_doc.class, LoaderInstances.uristrtypeFalseTrueNone,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `class` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
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

    let inputs
    try {
      inputs = await loadField(_doc.inputs, LoaderInstances.idmapinputsarrayOfWorkflowInputParameterLoader,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `inputs` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let outputs
    try {
      outputs = await loadField(_doc.outputs, LoaderInstances.idmapoutputsarrayOfWorkflowOutputParameterLoader,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `outputs` field is not valid because: ', [e])
        )
      } else {
        throw e
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

    let steps
    try {
      steps = await loadField(_doc.steps, LoaderInstances.idmapstepsunionOfarrayOfWorkflowStepLoader,
        baseuri, loadingOptions)
    } catch (e) {
      if (e instanceof ValidationException) {
        __errors.push(
          new ValidationException('the `steps` field is not valid because: ', [e])
        )
      } else {
        throw e
      }
    }

    let report
    if ('report' in _doc) {
      try {
        report = await loadField(_doc.report, LoaderInstances.unionOfundefinedtypeOrReportLoader,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `report` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let tags
    if ('tags' in _doc) {
      try {
        tags = await loadField(_doc.tags, LoaderInstances.unionOfarrayOfstrtypeOrundefinedtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `tags` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let creator
    if ('creator' in _doc) {
      try {
        creator = await loadField(_doc.creator, LoaderInstances.unionOfundefinedtypeOranyType,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `creator` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let license
    if ('license' in _doc) {
      try {
        license = await loadField(_doc.license, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `license` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let release
    if ('release' in _doc) {
      try {
        release = await loadField(_doc.release, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `release` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!GalaxyWorkflow.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`id\`,\`label\`,\`doc\`,\`inputs\`,\`outputs\`,\`uuid\`,\`class\`,\`steps\`,\`report\`,\`tags\`,\`creator\`,\`license\`,\`release\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'GalaxyWorkflow'", __errors)
    }

    const schema = new GalaxyWorkflow({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      id: id,
      label: label,
      doc: doc,
      inputs: inputs,
      outputs: outputs,
      uuid: uuid,
      class_: class_,
      steps: steps,
      report: report,
      tags: tags,
      creator: creator,
      license: license,
      release: release
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
                
    if (this.class_ != null) {
      const u = saveRelativeUri(this.class_, this.id, false,
                                relativeUris, undefined)
      if (u != null) {
        r.class = u
      }
    }
                
    if (this.label != null) {
      r.label = save(this.label, false, this.id, relativeUris)
    }
                
    if (this.doc != null) {
      r.doc = save(this.doc, false, this.id, relativeUris)
    }
                
    if (this.inputs != null) {
      r.inputs = save(this.inputs, false, this.id, relativeUris)
    }
                
    if (this.outputs != null) {
      r.outputs = save(this.outputs, false, this.id, relativeUris)
    }
                
    if (this.uuid != null) {
      r.uuid = save(this.uuid, false, this.id, relativeUris)
    }
                
    if (this.steps != null) {
      r.steps = save(this.steps, false, this.id, relativeUris)
    }
                
    if (this.report != null) {
      r.report = save(this.report, false, this.id, relativeUris)
    }
                
    if (this.tags != null) {
      r.tags = save(this.tags, false, this.id, relativeUris)
    }
                
    if (this.creator != null) {
      r.creator = save(this.creator, false, this.id, relativeUris)
    }
                
    if (this.license != null) {
      r.license = save(this.license, false, this.id, relativeUris)
    }
                
    if (this.release != null) {
      r.release = save(this.release, false, this.id, relativeUris)
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
            
  static attr: Set<string> = new Set(['id','label','doc','inputs','outputs','uuid','class','steps','report','tags','creator','license','release'])
}
