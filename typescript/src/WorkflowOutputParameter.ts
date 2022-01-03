
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
 * Auto-generated class implementation for https://galaxyproject.org/gxformat2/v19_09#WorkflowOutputParameter
 *
 * Describe an output parameter of a workflow.  The parameter must be
 * connected to one parameter defined in the workflow that
 * will provide the value of the output parameter. It is legal to
 * connect a WorkflowInputParameter to a WorkflowOutputParameter.
 * 
 */
export class WorkflowOutputParameter extends Saveable implements Internal.WorkflowOutputParameterProperties {
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


  constructor ({loadingOptions, extensionFields, id, label, doc, outputSource, type} : {loadingOptions?: LoadingOptions} & Internal.WorkflowOutputParameterProperties) {
    super(loadingOptions)
    this.extensionFields = extensionFields ?? {}
    this.id = id
    this.label = label
    this.doc = doc
    this.outputSource = outputSource
    this.type = type
  }

  /**
   * Used to construct instances of {@link WorkflowOutputParameter }.
   *
   * @param __doc                           Document fragment to load this record object from.
   * @param baseuri                         Base URI to generate child document IDs against.
   * @param loadingOptions                  Context for loading URIs and populating objects.
   * @param docRoot                         ID at this position in the document (if available)
   * @returns                               An instance of {@link WorkflowOutputParameter }
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

    let outputSource
    if ('outputSource' in _doc) {
      try {
        outputSource = await loadField(_doc.outputSource, LoaderInstances.unionOfundefinedtypeOrstrtype,
          baseuri, loadingOptions)
      } catch (e) {
        if (e instanceof ValidationException) {
          __errors.push(
            new ValidationException('the `outputSource` field is not valid because: ', [e])
          )
        } else {
          throw e
        }
      }
    }

    let type
    if ('type' in _doc) {
      try {
        type = await loadField(_doc.type, LoaderInstances.typedslunionOfundefinedtypeOrGalaxyTypeLoader2,
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

    const extensionFields: Dictionary<any> = {}
    for (const [key, value] of Object.entries(_doc)) {
      if (!WorkflowOutputParameter.attr.has(key)) {
        if ((key as string).includes(':')) {
          const ex = expandUrl(key, '', loadingOptions, false, false)
          extensionFields[ex] = value
        } else {
          __errors.push(
            new ValidationException(`invalid field ${key as string}, \
            expected one of: \`label\`,\`doc\`,\`id\`,\`outputSource\`,\`type\``)
          )
          break
        }
      }
    }

    if (__errors.length > 0) {
      throw new ValidationException("Trying 'WorkflowOutputParameter'", __errors)
    }

    const schema = new WorkflowOutputParameter({
      extensionFields: extensionFields,
      loadingOptions: loadingOptions,
      label: label,
      doc: doc,
      id: id,
      outputSource: outputSource,
      type: type
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
                
    if (this.outputSource != null) {
      r.outputSource = save(this.outputSource, false, this.id, relativeUris)
    }
                
    if (this.type != null) {
      r.type = save(this.type, false, this.id, relativeUris)
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
            
  static attr: Set<string> = new Set(['label','doc','id','outputSource','type'])
}
